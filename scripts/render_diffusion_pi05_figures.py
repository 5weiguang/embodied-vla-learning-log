"""Original teaching diagrams; no model runs. Reuses the repository drawing style."""
from pathlib import Path
import argparse
import math
import render_pi0_figures as d

ROOT = Path(__file__).resolve().parent.parent

def panel(folder, name, title, subtitle, cards, source):
    height = 280 + len(cards) * 220
    im, draw = d.canvas(1, title, subtitle, height)
    for i, (heading, body) in enumerate(cards):
        y = 190 + i * 220
        d.card(draw, (110, y, 1690, y + 175), heading, body,
               d.LIGHT_TEAL if i % 2 else d.LIGHT_BLUE,
               d.TEAL if i % 2 else d.BLUE)
        if i < len(cards)-1:
            d.arrow(draw, [(900, y+175), (900, y+215)])
    d.footer(draw, height, source)
    out = ROOT / 'assets' / folder
    out.mkdir(parents=True, exist_ok=True)
    im.save(out / (name + '.png'))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--font', type=Path, default=Path('C:/Windows/Fonts/msyh.ttc'))
    d.FONT = parser.parse_args().font
    panel('diffusion-policy','representations','多峰动作：平均值可能不是有效动作','教学示意：相同观测下，左右绕行都合理；不代表实测成功率。',[
      ('单点动作回归', '同一条件的目标为 −1 或 +1，等概率时平方误差最优预测为 0；0 可能穿过障碍。'),
      ('显式分布 / 隐式能量', '显式策略也可以输出混合高斯或分类概率；隐式策略通过能量函数搜索动作。'),
      ('条件扩散', '从随机动作序列开始，依据同一观测逐步去噪，得到一条一致的候选轨迹。')],
      '自绘解释图｜依据 Diffusion Policy v5 Figure 1、§2；不是论文原图。')
    panel('diffusion-policy','loop','预测一段，执行一段，再看环境','To=2、Tp=12、Ta=4 为教学参数；具体数据窗口对齐以实现为准。',[
      ('观测窗口 To=2', '机器人时间 t−1、t 的图像 / 状态 → 编码一次 → 条件特征 O_t'),
      ('预测窗口 Tp=12', '随机 A^K → εθ(O_t, A^k, k) → … → A^0：联合生成 12 个动作槽位'),
      ('执行窗口 Ta=4', '从对齐到当前时刻的可执行片段取 4 步；剩余预测不强制全部执行。'),
      ('反馈与重新规划', '获得新观测，重复生成；机器人时刻 t 与去噪等级 k 是两条不同的时间轴。')],
      '自绘解释图｜依据 Diffusion Policy v5 Figure 2、§2.3。')
    panel('diffusion-policy','training','训练噪声预测，不是回归平均动作','教学公式使用标准 DDPM 记号；不同于正文的简写调度系数。',[
      ('前向：人为构造监督任务', 'x_k = √ᾱ_k x_0 + √(1−ᾱ_k) ε；ε 是人为采样的动作空间高斯噪声。'),
      ('训练：比较加入的噪声与预测噪声', '条件为观测、带噪动作和等级 k；目标为 ε；优化噪声 MSE。'),
      ('算例与推理', 'x_0=4，ᾱ=0.36，ε=1 → x_k=2.4+0.8=3.2。推理从随机噪声出发。')],
      '自绘教学算例｜依据 v5 §2；算例来自用户学习记录，非模型实验。')
    panel('diffusion-policy','efficiency','三种旋钮，改变的是三件事','不要把控制周期、动作执行窗口和模型计算耗时混为一谈。',[
      ('减少去噪调用：DDIM', '固定已训练模型和噪声调度，用合适的跳步采样器减少推理调用。'),
      ('减少重复编码：缓存观测特征', '同一轮采样的观测不变，视觉编码一次；去噪网络仍需多次调用。'),
      ('改变执行窗口：Ta', 'Ta 小：更频繁重新观测规划；Ta 大：更长承诺执行。计算延迟另行测量。')],
      '自绘解释图｜依据 v5 §2.3、§3.4、Figure 5；未测 CPU 延迟。')
    panel('pi0.5','pipeline','π0.5：先选子任务，再生成动作','高低层属于同一模型系统，但使用不同的条件调用。',[
      ('观测 + 总任务 → 高层文本', '图像、本体状态、“收拾厨房” → 预测“把杯子放到水槽”。'),
      ('观测 + 子任务 + 带噪动作 → 动作专家', '预测连续场，经多次积分生成动作块；FAST 不负责高层规划。'),
      ('动作执行 → 新观测', '环境变化后继续决策；部署不要求人逐步提供训练期的 VI 标签。')],
      '自绘解释图｜依据 π0.5 v1 §IV-A/B、Figure 3；非运行轨迹。')
    panel('pi0.5','data','六类数据：不同来源，互补监督','主要侧重不意味着只贡献一种能力；HL 与机器人数据可以重叠。',[
      ('MM / ME / CE：机器人动作经验', 'MM：移动家庭操作；ME：多环境固定机械臂；CE：实验室跨本体与 OXE。'),
      ('HL / VI：高层决策监督', 'HL：示范上的子任务与相关标注；VI：人指导已有低层策略时提供的有效子任务。'),
      ('WD：视觉语言知识', '图像描述、问答、定位等任务；语义识别正确并不保证动作执行成功。')],
      '自绘分类图｜依据 π0.5 v1 §IV-C/D、Figure 4。')
    panel('pi0.5','stages','两阶段：离散学习与连续执行','FAST 编码动作标签；交叉熵还监督文本、定位、高层任务等。',[
      ('预训练：280k 步，α=0', 'MM + ME + CE + HL + WD；离散 token 预测；没有连续动作专家损失。'),
      ('后训练：80k 步，α=10', 'L = L_CE + α L_FM；加入动作专家，保留离散监督；加入 VI，移除 CE。'),
      ('推理：高层文本 + 连续动作', '文本自回归解码；连续动作使用 10 次去噪 / 积分调用，不是 10 个控制周期。')],
      '自绘解释图｜依据 π0.5 v1 §IV-B/D，Equation (1)。')
    panel('pi0.5','flow','插值方向与预测目标必须分开','这是用户答题的数值算例，不是训练日志或真实机器人轨迹。',[
      ('噪声 ω=2 → 动作 a=8', 'x(τ)=τa+(1−τ)ω；τ=0.25 时 x=3.5。τ 越大，越接近动作。'),
      ('插值导数：a−ω=+6', '沿着 τ 从 0 增加到 1 的方向，状态从 2 增加到 8。'),
      ('论文 Equation (1) 的目标：ω−a=−6', '它与上述导数相反。实现采样时需匹配时间方向及更新符号，不能直接照抄混用。')],
      '自绘教学算例｜依据 π0.5 v1 §IV-B；原文符号与导数显式区分。')
    panel('pi0.5','evidence','实验链：每张图回答不同问题','以下是实验问题地图，不是把不同指标合并成一个成功率。',[
      ('Figures 6–9：环境与泛化', '真实家庭和测试布置 → 训练地点数量 → 任务进度 / 选对物体 / 成功放置。'),
      ('Figures 10–12：数据与系统', '去掉数据源后性能怎样变化？完整训练系统与基线差异有多少混杂因素？'),
      ('Figure 13：高层监督与推理', '显式 / 隐式高层、去掉 HL / VI / WD；区分经验结果与表征机制推测。')],
      '自绘证据索引｜依据 π0.5 v1 §V；精确数值请读原图，未估读柱高。')
    h=1090
    im, draw=d.canvas(6,'注意力：读取方向与两种泄漏','组级解释性简化；行是读取者，列是被读取对象。',h)
    labels=['P：观测 / 提示','F：FAST 动作','A：连续动作']
    values=[['允许','禁止','禁止'],['允许','仅因果前缀','禁止'],['允许','禁止','允许（双向）']]
    for j, label in enumerate(labels):
        d.label(draw,(640+j*370,220),label,27,d.INK,'ma')
    for i,label in enumerate(labels):
        d.label(draw,(100,330+i*150),label,29)
        for j,v in enumerate(values[i]):
            x=470+j*370; y=295+i*150
            d.card(draw,(x,y,x+340,y+110),v,'',d.LIGHT_AMBER if v=='禁止' else d.LIGHT_TEAL)
    d.paragraph(draw,(110,790,1690,950),'F 内部因果遮蔽：不能偷看未来动作标签。\nA 与 F 隔离：不能把真实 FAST 标签当作连续动作推理时可用的条件。',32)
    d.footer(draw,h,'自绘简化矩阵｜依据 π0.5 v1 Appendix E、Figure 18；非源代码逐元素掩码。')
    im.save(ROOT/'assets/pi0.5/mask.png')
    # Geometric illustration: hand-defined paths, never fitted or simulated.
    im, draw=d.canvas(5,'绕障与均值：图上看见多峰问题','解析构造的教学路径，不是专家数据，也不是 DDPM 采样结果。',1000)
    draw.rounded_rectangle((190,200,1610,760),radius=20,fill='white',outline=d.GRAY,width=3)
    draw.ellipse((755,360,1045,650),fill=d.LIGHT_AMBER,outline=d.AMBER,width=4)
    d.label(draw,(900,500),'障碍',38,d.AMBER,'mm')
    for sign,color in [(-1,d.BLUE),(1,d.TEAL)]:
        pts=[(900+sign*420*math.sin(math.pi*i/100),700-440*i/100) for i in range(101)]
        draw.line(pts,fill=color,width=10)
    for y in range(270,700,32):
        draw.line((900,y,900,y+17),fill='#bd4444',width=8)
    for xy,txt in [((900,720),'起点'),((900,230),'终点')]:
        d.label(draw,xy,txt,30,d.INK,'mm')
    d.label(draw,(360,470),'模式一',32,d.BLUE)
    d.label(draw,(1300,470),'模式二',32,d.TEAL)
    d.paragraph(draw,(150,795,1650,900),'同一条件下两条路径都绕开障碍；逐时刻平均落在中间红线，可能不可执行。\n这说明单点均方误差的风险，不说明所有显式策略都失败。',30)
    d.footer(draw,1000,'原创教学几何图｜依据 v5 Figure 1 的多模态问题；坐标与路径人为构造。')
    im.save(ROOT/'assets/diffusion-policy/modes.png')
    im, draw=d.canvas(6,'滚动执行：只承诺预测的一部分','简化对齐到当前时刻；忽略实现中可能存在的历史动作槽位。',860)
    for row,(label,count,offset) in enumerate([('观测 To=2',2,-1),('预测 Tp=12',12,0),('执行 Ta=4',4,0)]):
        y=250+row*160
        d.label(draw,(75,y+30),label,32)
        for k in range(count):
            x=430+(k+offset)*100
            fill=d.LIGHT_TEAL if row==2 else d.LIGHT_BLUE
            draw.rounded_rectangle((x,y,x+85,y+85),radius=8,fill=fill,outline=d.TEAL,width=2)
            d.label(draw,(x+42,y+42),str(k+offset),26,d.INK,'mm')
    d.paragraph(draw,(100,725,1690,775),'列为相对物理时刻：执行 0–3 后，在新的观测条件下重规划，不强制执行旧预测的 4–11。',29)
    d.footer(draw,860,'原创时域示意｜依据 v5 §2.3；2/12/4 为教学参数，不是统一官方配置。')
    im.save(ROOT/'assets/diffusion-policy/horizon.png')
    print('Rendered 12 teaching diagrams; no model experiment.')

if __name__=='__main__':
    main()

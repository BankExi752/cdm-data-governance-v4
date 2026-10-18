// 数据资产化与知识资产化仿真实验 —— 业务类型与示例数据
// EXPORTS: ICaseIndustry, IDataAsset, IAssetCategory, ICodePair, IMaskField, IAnnoTask,
//          IUsageOffer, IValuationDim, IAuditEntry, IAuditKind, ILabState,
//          IRiskEvent, IRiskState, IAuditKind,
//          CASES, ASSETS_BY_CASE, CODE_PAIRS, MASK_FIELDS, ANNO_TASKS, USAGE_OFFERS,
//          VALUATION_DIMS, RISK_EVENTS, ROLE_OPTIONS, TARGET_OPTIONS,
//          INITIAL_BUDGET, MAX_PLATFORM_FEE

export const INITIAL_BUDGET = 500; // 万元
export const MAX_PLATFORM_FEE = 20; // 标注平台基础费（万元）

// 实验者角色（对应 V8.1 步骤0）
export const ROLE_OPTIONS = [
  { id: 'steward', label: '数据管家', desc: '数据治理与合规，守住底线' },
  { id: 'pm', label: '数据产品经理', desc: '数据变现与运营，放大价值' },
  { id: 'cdo', label: '首席数据官', desc: '统筹全局，人单合一' },
] as const;

// "人单合一"经营目标（对应 V8.1 步骤0）
export const TARGET_OPTIONS = [
  { id: 'cost', label: '降本增效', desc: '省 50 万治理成本' },
  { id: 'compliance', label: '合规避险', desc: '规避 100 万罚款风险' },
  { id: 'value', label: '价值创造', desc: '年增收 200 万' },
] as const;

export interface ICaseIndustry {
  id: string;
  name: string;
  sector: string;
  desc: string;
  scenes: string[];
}

export type IAssetCategory = 'structured' | 'unstructured' | 'semi';

export interface IDataAsset {
  id: string;
  name: string;
  category: IAssetCategory;
  desc: string;
  price: number; // 万元
  result: string; // 采购入库后的具体结果
}

export interface ICodePair {
  id: string;
  a: string;
  b: string;
  hint: string;
  same: boolean; // 正确答案：是否同一设备
}

export interface IMaskField {
  id: string;
  name: string;
  category: 'person' | 'finance' | 'location' | 'device';
  sensitive: boolean; // 是否需要脱敏
}

export interface IAnnoTask {
  id: string;
  name: string;
  desc: string;
  unit: string;
  unitPrice: number; // 万元 / 单位
}

export interface IUsageOffer {
  id: string;
  name: string;
  desc: string;
  cost: number; // 万元
  incomePerYear: number; // 万元/年
  deliverables: string[]; // 部署后的具体交付物
}

export interface IValuationDim {
  id: string;
  name: string;
  desc: string;
}

export type IAuditKind = 'system' | 'purchase' | 'govern' | 'usage' | 'income' | 'error' | 'risk';

export interface IAuditEntry {
  id: string;
  time: string;
  kind: IAuditKind;
  label: string;
  detail: string;
  amount: number; // 负=支出，正=收入，0=无金额
  undoable: boolean;
  rolledBack: boolean;
}

// 风险事件选项（每个选项对应不同的支出 / 年收入增量）
export interface IRiskOption {
  label: string;
  desc: string;
  cost: number; // 万元（正=支出）
  incomeDelta: number; // 万元/年（正=增收，负=减收）
}

// 风险事件定义（对应 V8.1 步骤12 的风险事件博弈）
export interface IRiskEvent {
  id: string;
  title: string;
  desc: string;
  options: IRiskOption[];
}

// 风险事件在实验中的状态
export interface IRiskState {
  eventId: string;
  resolved: boolean;
  choiceIndex: number | null;
}

export interface ILabState {
  caseId: string | null;
  budget: number;
  started: boolean;
  role: string | null; // 实验者角色 id
  target: string | null; // 经营目标 id
  purchased: string[]; // 资产 id
  cleaned: boolean; // 同质异码清洗完成
  masked: boolean; // 脱敏完成
  traced: boolean; // 可信溯源部署
  labeled: boolean; // 质检标注完成
  graphBuilt: boolean;
  algorithmBought: boolean;
  expertHired: boolean;
  risks: IRiskState[]; // 风险事件处理状态
  audit: IAuditEntry[];
}

export const CASES: ICaseIndustry[] = [
  {
    id: 'shuneng',
    name: '蜀能智造',
    sector: '未来能源 · 绿色氢能',
    desc: '电解槽制造与加氢站运营，设备多、系统杂，编码口径混乱',
    scenes: ['电解槽运行日志', '加氢站订单', '电堆外观图', '巡检视频'],
  },
  {
    id: 'shuguang',
    name: '蜀光智算',
    sector: '未来信息 · 6G 算力',
    desc: '智算中心建设与运维，算力调度与合同文档并存',
    scenes: ['算力调度日志', '机柜能耗表', '机房监控图像', '合同文档'],
  },
  {
    id: 'shugong',
    name: '蜀工智能',
    sector: '未来制造 · 机器人',
    desc: '工业机器人本体与产线集成，传感器与图纸海量',
    scenes: ['机器人关节日志', '产线订单', '零件外观图', '设计图纸'],
  },
  {
    id: 'shukang',
    name: '蜀康生命',
    sector: '未来健康 · 脑机接口',
    desc: '脑机接口设备研发与临床数据，隐私合规要求极高',
    scenes: ['脑电信号流', '临床试验表', '影像切片', '受试者文档'],
  },
];

// 每行业 6 类差异化数据资产（结构化×2 + 非结构化×2 + 半结构化×2）
// 对应 V8.1 数据层：四行业 × 六类数据，价格/内容随行业切换
export const ASSETS_BY_CASE: Record<string, IDataAsset[]> = {
  // 未来能源 · 绿色氢能（蜀能智造）
  shuneng: [
    {
      id: 'a-log',
      name: '电解槽运行日志',
      category: 'structured',
      desc: 'IoT 网关 + 传感器：温度/压力/电流时序',
      price: 20,
      result: '入库 1.2 万条电解槽时序记录，覆盖温度/压力/电流 3 类传感器字段，支持故障预测训练',
    },
    {
      id: 'a-order',
      name: '加氢站订单表',
      category: 'structured',
      desc: 'ERP 直连：客户/频次/金额',
      price: 15,
      result: '入库 8.5 万条加氢订单记录，含客户、加注频次、金额字段，支撑经营分析',
    },
    {
      id: 'a-img',
      name: '电堆外观图',
      category: 'unstructured',
      desc: '工业相机采集：双极板缺陷/腐蚀/裂纹',
      price: 25,
      result: '入库 6,000 张电堆工业图像，已自动打标 4 类缺陷，可用于 2D 图像标注训练',
    },
    {
      id: 'a-video',
      name: '加氢站巡检视频',
      category: 'unstructured',
      desc: '防爆摄像系统：管线泄漏检测',
      price: 35,
      result: '入库 800 段巡检视频（约 120 小时），已完成切片与关键帧抽取',
    },
    {
      id: 'a-contract',
      name: '氢能装备合同文档',
      category: 'semi',
      desc: '法务归档：条款/金额/质保',
      price: 18,
      result: '入库 4,200 份装备合同，OCR 解析完成，抽取条款/金额/质保实体',
    },
    {
      id: 'a-logfile',
      name: '加氢站操作日志',
      category: 'semi',
      desc: '文本+时序混合：告警/状态/事件',
      price: 12,
      result: '入库 3.6 万条操作日志，告警/状态/事件字段已结构化，可用于异常检测',
    },
  ],
  // 未来信息 · 6G 算力（蜀光智算）
  shuguang: [
    {
      id: 'a-log',
      name: '算力调度日志',
      category: 'structured',
      desc: '调度中心：任务队列/算力分配/时延',
      price: 20,
      result: '入库 1.2 万条调度时序记录，覆盖队列/分配/时延 3 类字段，支持算力预测训练',
    },
    {
      id: 'a-order',
      name: '机柜能耗表',
      category: 'structured',
      desc: 'DCIM 直连：PUE/功耗/温湿度',
      price: 15,
      result: '入库 8.5 万条能耗记录，含 PUE、功耗、温湿度字段，支撑能效优化分析',
    },
    {
      id: 'a-img',
      name: '机房监控图像',
      category: 'unstructured',
      desc: '巡检机器人采集：服务器状态/指示灯异常',
      price: 25,
      result: '入库 6,000 张机房图像，已自动打标 4 类异常，可用于 2D 图像标注训练',
    },
    {
      id: 'a-video',
      name: '网络抓包视频流',
      category: 'unstructured',
      desc: '核心网探针：流量特征/攻击行为',
      price: 35,
      result: '入库 800 段抓包视频（约 120 小时），已完成协议解析与关键帧抽取',
    },
    {
      id: 'a-contract',
      name: '算力合同文档',
      category: 'semi',
      desc: '法务归档：条款/SLA/金额',
      price: 18,
      result: '入库 4,200 份算力合同，OCR 解析完成，抽取条款/SLA/金额实体',
    },
    {
      id: 'a-logfile',
      name: '审计日志',
      category: 'semi',
      desc: '安全审计：操作/权限/事件',
      price: 12,
      result: '入库 3.6 万条审计日志，操作/权限/事件字段已结构化，可用于安全检测',
    },
  ],
  // 未来制造 · 机器人（蜀工智能）
  shugong: [
    {
      id: 'a-log',
      name: '机器人关节力矩日志',
      category: 'structured',
      desc: '伺服驱动器：力矩/速度/位置时序',
      price: 20,
      result: '入库 1.2 万条关节时序记录，覆盖力矩/速度/位置 3 类字段，支持故障预测训练',
    },
    {
      id: 'a-order',
      name: '产线订单表',
      category: 'structured',
      desc: 'MES 直连：工单/交期/批次',
      price: 15,
      result: '入库 8.5 万条产线订单记录，含工单、交期、批次字段，支撑排产分析',
    },
    {
      id: 'a-img',
      name: '零件外观图',
      category: 'unstructured',
      desc: '机器视觉采集：毛刺/划痕/装配缺陷',
      price: 25,
      result: '入库 6,000 张零件图像，已自动打标 4 类缺陷，可用于 2D 图像标注训练',
    },
    {
      id: 'a-video',
      name: '训练场动作视频',
      category: 'unstructured',
      desc: '动作捕捉：示教轨迹/异常姿态',
      price: 35,
      result: '入库 800 段动作视频（约 120 小时），已完成姿态解算与关键帧抽取',
    },
    {
      id: 'a-contract',
      name: '设计图纸文档',
      category: 'semi',
      desc: 'PLM 归档：BOM/版本/变更',
      price: 18,
      result: '入库 4,200 份图纸文档，解析完成，抽取 BOM/版本/变更实体',
    },
    {
      id: 'a-logfile',
      name: '质检记录',
      category: 'semi',
      desc: '质量追溯：检测项/结果/责任人',
      price: 12,
      result: '入库 3.6 万条质检记录，检测项/结果/责任人字段已结构化，可用于质量分析',
    },
  ],
  // 未来健康 · 脑机接口（蜀康生命）
  shukang: [
    {
      id: 'a-log',
      name: '脑电信号流',
      category: 'structured',
      desc: '脑机接口：EEG 波形/频段/事件',
      price: 20,
      result: '入库 1.2 万条脑电时序记录，覆盖 EEG 波形/频段/事件 3 类字段，支持意图识别训练',
    },
    {
      id: 'a-order',
      name: '临床试验表',
      category: 'structured',
      desc: 'EDC 直连：受试者/访视/终点',
      price: 15,
      result: '入库 8.5 万条临床试验记录，含受试者、访视、终点字段，支撑疗效分析',
    },
    {
      id: 'a-img',
      name: '影像切片',
      category: 'unstructured',
      desc: '医学影像采集：病灶/组织/标记',
      price: 25,
      result: '入库 6,000 张影像切片，已自动打标 4 类病灶，可用于 2D 图像标注训练',
    },
    {
      id: 'a-video',
      name: '康复训练视频',
      category: 'unstructured',
      desc: '动作捕捉：康复进度/异常姿态',
      price: 35,
      result: '入库 800 段康复视频（约 120 小时），已完成姿态解算与关键帧抽取',
    },
    {
      id: 'a-contract',
      name: '受试者知情同意文档',
      category: 'semi',
      desc: '伦理归档：授权/风险/去标识',
      price: 18,
      result: '入库 4,200 份知情同意文档，解析完成，抽取授权/风险/去标识实体',
    },
    {
      id: 'a-logfile',
      name: '临床量表',
      category: 'semi',
      desc: '随访记录：评分/备注/随访人',
      price: 12,
      result: '入库 3.6 万条量表记录，评分/备注/随访人字段已结构化，可用于疗效分析',
    },
  ],
};

// 按行业取资产（兼容未选行业时的默认）
export function getAssets(caseId: string | null): IDataAsset[] {
  return (caseId && ASSETS_BY_CASE[caseId]) || ASSETS_BY_CASE.shuneng;
}

export const CODE_PAIRS: ICodePair[] = [
  {
    id: 'p1',
    a: '电堆A',
    b: '燃料电池A',
    hint: '电堆A 出自工艺台账，燃料电池A 出自质量系统，两者铭牌序列号一致',
    same: true,
  },
  {
    id: 'p2',
    a: '压缩机01',
    b: 'CMP-001',
    hint: '压缩机01 出自巡检台账，CMP-001 出自备件系统，型号与安装位置相同',
    same: true,
  },
  {
    id: 'p3',
    a: '储氢罐3号',
    b: 'TK-H2-03',
    hint: '储氢罐3号 出自压力容器档案，TK-H2-03 出自 EAM 系统，出厂编号相同',
    same: true,
  },
  {
    id: 'p4',
    a: '传感器X',
    b: 'Sensor-7',
    hint: '传感器X 出自 SCADA，Sensor-7 出自仪表台账，量程与安装点位均不同',
    same: false,
  },
];

export const MASK_FIELDS: IMaskField[] = [
  { id: 'f-name', name: '客户姓名', category: 'person', sensitive: true },
  { id: 'f-idcard', name: '客户身份证号', category: 'person', sensitive: true },
  { id: 'f-bank', name: '银行账号', category: 'finance', sensitive: true },
  { id: 'f-amount', name: '合同金额', category: 'finance', sensitive: true },
  { id: 'f-loc', name: '人员定位', category: 'location', sensitive: true },
  { id: 'f-temp', name: '设备温度', category: 'device', sensitive: false },
  { id: 'f-pressure', name: '压力读数', category: 'device', sensitive: false },
  { id: 'f-deviceid', name: '设备编号', category: 'device', sensitive: false },
];

export const ANNO_TASKS: IAnnoTask[] = [
  {
    id: 't-box',
    name: '2D 图像框选',
    desc: '电堆外观缺陷框选：裂纹/腐蚀/划痕',
    unit: '张',
    unitPrice: 0.02,
  },
  {
    id: 't-text',
    name: '文本转写与实体标注',
    desc: '巡检记录转写，标注设备/时间/异常',
    unit: '条',
    unitPrice: 0.01,
  },
  {
    id: 't-voice',
    name: '语音告警转写',
    desc: '操作语音日志转写与事件对齐',
    unit: '条',
    unitPrice: 0.015,
  },
];

export const USAGE_OFFERS: IUsageOffer[] = [
  {
    id: 'u-graph',
    name: '企业知识图谱',
    desc: '构建设备/项目/人员/标签的语义图谱，支撑语义检索',
    cost: 30,
    incomePerYear: 0,
    deliverables: [
      '抽取实体 1.2 万个（设备 4,800 · 项目 320 · 人员 1,600 · 标签 5,300）',
      '构建关系边 3.5 万条，实体与文档双向关联',
      '开放语义检索：支持「找到所有 2026 年检修过的压缩机」类查询',
      '对接 MCP Server，供智能体跨系统取数引用',
    ],
  },
  {
    id: 'u-algo',
    name: '故障预测算法',
    desc: '基于时序数据训练故障预测，每年带来算法服务收入',
    cost: 30,
    incomePerYear: 50,
    deliverables: [
      '故障预测模型上线，Top-1 准确率 87%，AUC 0.91',
      '接入设备运行日志等 3 类时序数据源，分钟级增量推理',
      '提前 2 小时预警设备故障，减少非计划停机',
      '模型 API 开放，形成算法服务收入 +50 万/年',
    ],
  },
  {
    id: 'u-expert',
    name: '算法专家优化',
    desc: '聘请行业算法专家调优模型与产线，每年带来咨询收入',
    cost: 40,
    incomePerYear: 60,
    deliverables: [
      '完成 3 个核心模型调优，推理时延降低 32%',
      '建立标注 SOP 与质检规则库，标注返工率下降 40%',
      '输出行业知识库与调优方法论，沉淀为可复用资产',
      '对外提供专家咨询服务，形成咨询收入 +60 万/年',
    ],
  },
];

export const VALUATION_DIMS: IValuationDim[] = [
  { id: 'd-usable', name: '可用性', desc: '数据集规模与字段完整，可被消费' },
  { id: 'd-trust', name: '可信性', desc: '来源可溯、质量可度量、有验收' },
  { id: 'd-complete', name: '完整性', desc: '口径统一，字段与标签可解释' },
  { id: 'd-trace', name: '可追溯性', desc: '版本、血缘、台账齐全，可回滚' },
  { id: 'd-std', name: '标准化', desc: '统一编码与主数据，消除同质异码' },
  { id: 'd-compliance', name: '合规性', desc: '脱敏、分级、权限与审计留痕' },
];

// 风险事件博弈（对应 V8.1 步骤12 三次估值迭代间的风险事件）
// 每次选择都真实影响预算与年收入，且全部留痕
export const RISK_EVENTS: IRiskEvent[] = [
  {
    id: 'r-1',
    title: '监管合规抽查',
    desc: '数据监管局抽查发现你的数据底座存在未脱敏字段外泄风险，要求限期整改，否则按上限罚款。',
    options: [
      { label: '立即补全脱敏', desc: '紧急追加脱敏规则，当场消除风险', cost: 20, incomeDelta: 0 },
      { label: '自查后整改', desc: '花时间自查，暴露面更大', cost: 40, incomeDelta: -10 },
      { label: '拖延应对', desc: '不正面回应，赌抽查结束', cost: 0, incomeDelta: -50 },
    ],
  },
  {
    id: 'r-2',
    title: '竞争对手抢数据',
    desc: '同行业对手高价挖你的标注团队，并向数据源厂商开出双倍价格抢购同源数据。',
    options: [
      { label: '加薪留人+签独家', desc: '锁定标注团队与数据源独家供应', cost: 30, incomeDelta: 0 },
      { label: '换开源替代源', desc: '改用开源数据，质量和独家性下降', cost: 10, incomeDelta: -20 },
      { label: '不设防', desc: '任由对手抢购，数据被截胡', cost: 0, incomeDelta: -40 },
    ],
  },
  {
    id: 'r-3',
    title: 'AI 算法事故',
    desc: '已上线的预测算法在生产中误报，引发产线停摆，客户要求追责赔偿。',
    options: [
      { label: '紧急回滚并修复', desc: '回滚模型、补充重训数据', cost: 25, incomeDelta: 0 },
      { label: '人工复核兜底', desc: '暂停自动决策，转人工审核', cost: 15, incomeDelta: -15 },
      { label: '继续运行', desc: '侥幸继续，事故扩大', cost: 0, incomeDelta: -60 },
    ],
  },
];

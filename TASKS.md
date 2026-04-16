# PulseScope 任务追踪

## Phase 1: 基础设施加固（进行中）

### P0 - 数据库层 ✅ 已完成
- [x] 添加 PostgreSQL/SQLite 双模式支持
- [x] 设计数据库 Schema（Company, Product, Event, RiskReport, CacheEntry 等）
- [x] 集成 SQLAlchemy ORM
- [x] 种子数据导入脚本（10家化工企业已入库）
- [ ] Alembic 迁移配置（待完善）

### P0 - 缓存层 ✅ 已完成
- [x] 添加 Redis + 内存缓存双模式
- [x] Tavily 搜索结果缓存接口（TTL: 1小时）
- [x] 风险报告缓存接口（TTL: 30分钟）
- [x] 知识图谱节点缓存接口（TTL: 24小时）
- [x] PostgreSQL 作为持久化缓存回退

### P1 - 异步架构（待开始）
- [ ] 集成 Celery + Redis 作为任务队列
- [ ] 将 ingestion/extraction 改造为异步任务
- [ ] API 改为异步返回 task_id
- [ ] 前端支持轮询/websocket 获取结果

### P1 - 生产级特性（待开始）
- [ ] 结构化日志（structlog）
- [ ] 基础监控指标（Prometheus 格式）
- [ ] 限流配置（slowapi）
- [ ] 健康检查端点扩展

## Phase 2: 数据层补强（待开始）
- [ ] 公告数据真实化（akshare + 巨潮资讯）
- [ ] 航运数据接入（MarineTraffic / AISHub）
- [ ] 期货/现货价格接入（akshare）
- [ ] 数据 ETL pipeline

## Phase 3: 知识图谱升级（待开始）
- [ ] 图模型重构（节点/关系类型扩展）
- [ ] 种子数据工业化（爬虫自动抓取）
- [ ] 考虑迁移到 Neo4j/Memgraph

## Phase 4: 推理引擎增强（待开始）
- [ ] 引入 RiskScorer 抽象层
- [ ] 实现 ShippingRiskScorer
- [ ] 实现 PriceRiskScorer
- [ ] LLM Prompt 优化（Chain-of-Thought）

## Phase 5: 前端增强（待开始）
- [ ] 风险趋势图表（recharts）
- [ ] 知识图谱可视化（react-force-graph）
- [ ] 航线地图（react-map-gl）
- [ ] 监控面板

## 已完成
- [x] 项目骨架搭建（core, api, skill, frontend）
- [x] 39个核心测试全绿
- [x] FastAPI + MCP Skill 双输出
- [x] Next.js 前端基础界面
- [x] Git push 到远程仓库
- [x] 新增 11 个数据库/缓存测试（共 50 个测试）
- [x] SQLite 开发模式 + 内存缓存（无需 Docker）

## 技术债务
- 需要 Docker 环境测试 PostgreSQL + Redis 生产配置
- 需要 Alembic 迁移脚本管理数据库变更
- 需要集成测试验证端到端流程

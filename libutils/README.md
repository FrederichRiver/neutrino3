# Jupiter
Jupiter是一个工具包。它包含了最基础的功能：
1. 网络功能：network
2. 任务管理功能：task manager
3. 数据库管理功能：database manager
4. 基本函数：utils
5. 交易日模型：trade date
---
Database manager模块
1. 获取需要备份的database名单，目前是写在代码当中，将来变为柔性配置。
2. 备份数据库
3. 将备份完成的数据库sql文件打包压缩，并用时间戳命名压缩包
4. 识别较旧的备份文件，将其删除。
---
Network模块  
该模块实现3项功能：  
1. Random Header：用于生成随机的Http header。这个模块将来会改名字。  
2. fetch_html_object：用于从Html对象中获得一个etree模型，用于后续的内容分析。  
3. delay：一个简单的延时功能。  
---
Message Manager模块
该模块用于向各类终端发送信息。
---
待开发功能：
1. 自动分析备份文件，清楚超过3天的文件
2. 每天自动将日志文件备份




CREATE TABLE `time_analysis` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `datetime` datetime DEFAULT NULL COMMENT '时间',
  `application_name` varchar(32) DEFAULT NULL COMMENT '应用名',
  `totalcount` int(8) DEFAULT NULL COMMENT '总请求数',
  `errorcount` int(8) DEFAULT NULL COMMENT '错误请求数',
  `median` int(5) DEFAULT NULL COMMENT '中位数',
  `average` int(5) DEFAULT NULL COMMENT '平均数',
  `distribution95` int(5) DEFAULT NULL COMMENT '95值',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1005 DEFAULT CHARSET=utf8mb4 COMMENT='数据分析结果存署表';

CREATE TABLE `application_list` (
  `application_name` varchar(32) NOT NULL,
  `service_type` varchar(32) DEFAULT NULL COMMENT '服务类型',
  `code` int(11) DEFAULT NULL COMMENT '服务类型代码',
  `agents` int(11) DEFAULT NULL COMMENT 'agent个数',
  `agentlists` varchar(256) DEFAULT NULL COMMENT 'agent list',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`application_name`),
  UNIQUE KEY `Unique_App` (`application_name`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='pinpoint app list';
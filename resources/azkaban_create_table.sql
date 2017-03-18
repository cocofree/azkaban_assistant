-- MySQL dump 10.13  Distrib 5.6.27, for Linux (x86_64)
--
-- Host: bhd02    Database: azkaban_meta
-- ------------------------------------------------------
-- Server version	5.6.20-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `active_executing_flows`
--

DROP TABLE IF EXISTS `active_executing_flows`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `active_executing_flows` (
  `exec_id` int(11) NOT NULL DEFAULT '0',
  `host` varchar(255) DEFAULT NULL,
  `port` int(11) DEFAULT NULL,
  `update_time` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`exec_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `active_sla`
--

DROP TABLE IF EXISTS `active_sla`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `active_sla` (
  `exec_id` int(11) NOT NULL,
  `job_name` varchar(128) NOT NULL,
  `check_time` bigint(20) NOT NULL,
  `rule` tinyint(4) NOT NULL,
  `enc_type` tinyint(4) DEFAULT NULL,
  `options` longblob NOT NULL,
  PRIMARY KEY (`exec_id`,`job_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `execution_flows`
--

DROP TABLE IF EXISTS `execution_flows`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `execution_flows` (
  `exec_id` int(11) NOT NULL AUTO_INCREMENT,
  `project_id` int(11) NOT NULL,
  `version` int(11) NOT NULL,
  `flow_id` varchar(128) NOT NULL,
  `status` tinyint(4) DEFAULT NULL,
  `submit_user` varchar(64) DEFAULT NULL,
  `submit_time` bigint(20) DEFAULT NULL,
  `update_time` bigint(20) DEFAULT NULL,
  `start_time` bigint(20) DEFAULT NULL,
  `end_time` bigint(20) DEFAULT NULL,
  `enc_type` tinyint(4) DEFAULT NULL,
  `flow_data` longblob,
  PRIMARY KEY (`exec_id`),
  KEY `ex_flows_start_time` (`start_time`),
  KEY `ex_flows_end_time` (`end_time`),
  KEY `ex_flows_time_range` (`start_time`,`end_time`),
  KEY `ex_flows_flows` (`project_id`,`flow_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `execution_jobs`
--

DROP TABLE IF EXISTS `execution_jobs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `execution_jobs` (
  `exec_id` int(11) NOT NULL,
  `project_id` int(11) NOT NULL,
  `version` int(11) NOT NULL,
  `flow_id` varchar(128) NOT NULL,
  `job_id` varchar(128) NOT NULL,
  `attempt` int(11) NOT NULL DEFAULT '0',
  `start_time` bigint(20) DEFAULT NULL,
  `end_time` bigint(20) DEFAULT NULL,
  `status` tinyint(4) DEFAULT NULL,
  `input_params` longblob,
  `output_params` longblob,
  `attachments` longblob,
  PRIMARY KEY (`exec_id`,`job_id`,`attempt`),
  KEY `exec_job` (`exec_id`,`job_id`),
  KEY `exec_id` (`exec_id`),
  KEY `ex_job_id` (`project_id`,`job_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `execution_logs`
--

DROP TABLE IF EXISTS `execution_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `execution_logs` (
  `exec_id` int(11) NOT NULL,
  `name` varchar(128) NOT NULL DEFAULT '',
  `attempt` int(11) NOT NULL DEFAULT '0',
  `enc_type` tinyint(4) DEFAULT NULL,
  `start_byte` int(11) NOT NULL DEFAULT '0',
  `end_byte` int(11) DEFAULT NULL,
  `log` longblob,
  `upload_time` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`exec_id`,`name`,`attempt`,`start_byte`),
  KEY `ex_log_attempt` (`exec_id`,`name`,`attempt`),
  KEY `ex_log_index` (`exec_id`,`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `kk_jobs`
--

DROP TABLE IF EXISTS `kk_jobs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `kk_jobs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL COMMENT '任务名，不能重复',
  `project_name` varchar(64) NOT NULL COMMENT '项目名，一个任务只能属于一个项目，防止多次运行',
  `flow_name` varchar(64) DEFAULT '' COMMENT '流程中的最后的节点任务名，空为节点，非空为子流程',
  `server_host` varchar(30) DEFAULT '' COMMENT '任务所在服务器域名，或IP',
  `server_user` varchar(30) DEFAULT '' COMMENT '执行任务的服务器用户',
  `server_dir` varchar(200) DEFAULT '' COMMENT '执行任务的服务器目录，有的话自动执行cd',
  `server_script` varchar(500) NOT NULL COMMENT '执行任务的脚本命令',
  `dependencies` varchar(2000) DEFAULT '' COMMENT '依赖的任务，多个则以逗号分隔',
  `success_email` varchar(2000) DEFAULT '' COMMENT '执行成功时的邮件接收人',
  `failure_email` varchar(2000) DEFAULT '' COMMENT '执行成功时的邮件接收人',
  `success_sms` varchar(2000) DEFAULT '' COMMENT '执行成功时的短信接收人',
  `failure_sms` varchar(2000) DEFAULT '' COMMENT '执行失败时的短信接收人',
  `retries` tinyint(2) DEFAULT '0' COMMENT '失败后的重试次数',
  `creator` varchar(30) DEFAULT '' COMMENT '任务创建人',
  `updater` varchar(30) DEFAULT '' COMMENT '修改人',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `loc` varchar(50) DEFAULT '' COMMENT 'DAG中的位置',
  `ext_dependencies` varchar(4000) DEFAULT '' COMMENT '外部依赖，针对跨任务及跨时间维度的任务',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `project_name` (`project_name`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COMMENT='自定义任务配置';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `kk_jobs_status`
--

DROP TABLE IF EXISTS `kk_jobs_status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `kk_jobs_status` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `job_name` varchar(200) NOT NULL COMMENT '任务名称',
  `execute_time` bigint(20) NOT NULL COMMENT '执行时间参数,只支持天级、小时级',
  `exec_id` bigint(20) DEFAULT '0' COMMENT 'azkaban任务ID',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '任务创建时间',
  `start_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '任务实际开始时间，所有依赖完成',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '任务更新时间',
  `status` int(11) NOT NULL DEFAULT '0' COMMENT '任务状态,0执行中，1成功，-1失败',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uni_job_exec` (`job_name`,`execute_time`),
  KEY `idx_job` (`job_name`),
  KEY `idx_execute_time` (`execute_time`),
  KEY `idx_status` (`status`),
  KEY `idx_exec_id` (`exec_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `project_events`
--

DROP TABLE IF EXISTS `project_events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `project_events` (
  `project_id` int(11) NOT NULL,
  `event_type` tinyint(4) NOT NULL,
  `event_time` bigint(20) NOT NULL,
  `username` varchar(64) DEFAULT NULL,
  `message` varchar(512) DEFAULT NULL,
  KEY `log` (`project_id`,`event_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `project_files`
--

DROP TABLE IF EXISTS `project_files`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `project_files` (
  `project_id` int(11) NOT NULL,
  `version` int(11) NOT NULL,
  `chunk` int(11) NOT NULL DEFAULT '0',
  `size` int(11) DEFAULT NULL,
  `file` longblob,
  PRIMARY KEY (`project_id`,`version`,`chunk`),
  KEY `file_version` (`project_id`,`version`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `project_flows`
--

DROP TABLE IF EXISTS `project_flows`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `project_flows` (
  `project_id` int(11) NOT NULL,
  `version` int(11) NOT NULL,
  `flow_id` varchar(128) NOT NULL DEFAULT '',
  `modified_time` bigint(20) NOT NULL,
  `encoding_type` tinyint(4) DEFAULT NULL,
  `json` blob,
  PRIMARY KEY (`project_id`,`version`,`flow_id`),
  KEY `flow_index` (`project_id`,`version`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `project_permissions`
--

DROP TABLE IF EXISTS `project_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `project_permissions` (
  `project_id` varchar(64) NOT NULL,
  `modified_time` bigint(20) NOT NULL,
  `name` varchar(64) NOT NULL,
  `permissions` int(11) NOT NULL,
  `isGroup` tinyint(1) NOT NULL,
  PRIMARY KEY (`project_id`,`name`),
  KEY `permission_index` (`project_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `project_properties`
--

DROP TABLE IF EXISTS `project_properties`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `project_properties` (
  `project_id` int(11) NOT NULL,
  `version` int(11) NOT NULL,
  `name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `modified_time` bigint(20) NOT NULL,
  `encoding_type` tinyint(4) DEFAULT NULL,
  `property` blob,
  PRIMARY KEY (`project_id`,`version`,`name`),
  KEY `idx_name` (`name`),
  KEY `properties_index` (`project_id`,`version`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `project_versions`
--

DROP TABLE IF EXISTS `project_versions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `project_versions` (
  `project_id` int(11) NOT NULL,
  `version` int(11) NOT NULL,
  `upload_time` bigint(20) NOT NULL,
  `uploader` varchar(64) NOT NULL,
  `file_type` varchar(16) DEFAULT NULL,
  `file_name` varchar(128) DEFAULT NULL,
  `md5` binary(16) DEFAULT NULL,
  `num_chunks` int(11) DEFAULT NULL,
  PRIMARY KEY (`project_id`,`version`),
  KEY `version_index` (`project_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `projects`
--

DROP TABLE IF EXISTS `projects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `projects` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `modified_time` bigint(20) NOT NULL,
  `create_time` bigint(20) NOT NULL,
  `version` int(11) DEFAULT NULL,
  `last_modified_by` varchar(64) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `enc_type` tinyint(4) DEFAULT NULL,
  `settings_blob` longblob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `project_id` (`id`),
  KEY `project_name` (`name`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `properties`
--

DROP TABLE IF EXISTS `properties`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `properties` (
  `name` varchar(64) NOT NULL,
  `type` int(11) NOT NULL,
  `modified_time` bigint(20) NOT NULL,
  `value` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`name`,`type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `schedules`
--

DROP TABLE IF EXISTS `schedules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `schedules` (
  `schedule_id` int(11) NOT NULL AUTO_INCREMENT,
  `project_id` int(11) NOT NULL,
  `project_name` varchar(128) NOT NULL,
  `flow_name` varchar(128) NOT NULL,
  `status` varchar(16) DEFAULT NULL,
  `first_sched_time` bigint(20) DEFAULT NULL,
  `timezone` varchar(64) DEFAULT NULL,
  `period` varchar(16) DEFAULT NULL,
  `last_modify_time` bigint(20) DEFAULT NULL,
  `next_exec_time` bigint(20) DEFAULT NULL,
  `submit_time` bigint(20) DEFAULT NULL,
  `submit_user` varchar(128) DEFAULT NULL,
  `enc_type` tinyint(4) DEFAULT NULL,
  `schedule_options` longblob,
  PRIMARY KEY (`schedule_id`),
  KEY `sched_project_id` (`project_id`,`flow_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `triggers`
--

DROP TABLE IF EXISTS `triggers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `triggers` (
  `trigger_id` int(11) NOT NULL AUTO_INCREMENT,
  `trigger_source` varchar(128) DEFAULT NULL,
  `modify_time` bigint(20) NOT NULL,
  `enc_type` tinyint(4) DEFAULT NULL,
  `data` longblob,
  PRIMARY KEY (`trigger_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-03-17 17:09:35

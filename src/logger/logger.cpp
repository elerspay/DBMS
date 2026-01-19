#include "logger.h"
#include <iostream>
#include <iomanip>
#include <cstring>
#include <sys/stat.h>

// 默认日志文件路径
static const char* DEFAULT_LOG_PATH = "../../logs/trivialdb.log";
static const char* DEFAULT_ERROR_LOG_PATH = "../../logs/trivialdb_error.log";

Logger::Logger() 
    // ========== 用户/权限系统接口预留 ==========
    // 当前写死为 "admin"，实现用户系统后通过 set_current_user() 动态设置
    // 未来扩展时，可在用户登录成功后调用:
    //   Logger::get_instance()->set_current_user(authenticated_user);
    : current_user("admin"),
    // ========================================
      current_database(""),
      min_level(LogLevel::DEBUG),
      console_output(false),
      initialized(false)
{
    log_file_path = DEFAULT_LOG_PATH;
    error_log_file_path = DEFAULT_ERROR_LOG_PATH;
}

Logger::~Logger()
{
    if (log_file.is_open()) {
        log_file.close();
    }
    if (error_log_file.is_open()) {
        error_log_file.close();
    }
}

void Logger::ensure_initialized()
{
    if (initialized) return;
    
    // 确保日志目录存在
    struct stat st;
    if (stat("../../logs", &st) != 0) {
        #ifdef _WIN32
        mkdir("../../logs");
        #else
        mkdir("../../logs", 0755);
        #endif
    }
    
    // 打开日志文件（追加模式）
    log_file.open(log_file_path, std::ios::app);
    error_log_file.open(error_log_file_path, std::ios::app);
    
    initialized = true;
    
    // 注意：这里不能调用 log()，否则会导致死锁
    // 因为 write_log() 已经持有锁，而 log() -> write_log() 会再次尝试获取锁
    // 直接写入启动日志
    if (log_file.is_open()) {
        log_file << "================================================================================" << std::endl;
        log_file << "[" << get_timestamp() << "] [INFO] [" << current_user << "] SYSTEM_START" << std::endl;
        log_file << "--------------------------------------------------------------------------------" << std::endl;
        log_file << "Database: -" << std::endl;
        log_file << "Status: SUCCESS" << std::endl;
        log_file << "Message: TrivialDB Logger initialized" << std::endl;
        log_file << "================================================================================" << std::endl;
        log_file << std::endl;
        log_file.flush();
    }
}

Logger* Logger::get_instance()
{
    static Logger instance;
    return &instance;
}

std::string Logger::get_timestamp()
{
    auto now = std::time(nullptr);
    auto tm = std::localtime(&now);
    
    std::ostringstream oss;
    oss << std::put_time(tm, "%Y-%m-%d %H:%M:%S");
    return oss.str();
}

std::string Logger::level_to_string(LogLevel level)
{
    switch (level) {
        case LogLevel::DEBUG:   return "DEBUG";
        case LogLevel::INFO:    return "INFO";
        case LogLevel::WARNING: return "WARNING";
        case LogLevel::ERROR:   return "ERROR";
        case LogLevel::FATAL:   return "FATAL";
        default:                return "UNKNOWN";
    }
}

std::string Logger::op_type_to_string(OperationType op)
{
    switch (op) {
        case OperationType::DB_CREATE:          return "DB_CREATE";
        case OperationType::DB_DROP:            return "DB_DROP";
        case OperationType::DB_USE:             return "DB_USE";
        case OperationType::DB_SHOW:            return "DB_SHOW";
        case OperationType::TABLE_CREATE:       return "TABLE_CREATE";
        case OperationType::TABLE_DROP:         return "TABLE_DROP";
        case OperationType::TABLE_SHOW:         return "TABLE_SHOW";
        case OperationType::TABLE_RENAME:       return "TABLE_RENAME";
        case OperationType::TABLE_ALTER_ADD:    return "TABLE_ALTER_ADD";
        case OperationType::TABLE_ALTER_DROP:   return "TABLE_ALTER_DROP";
        case OperationType::TABLE_ALTER_MODIFY: return "TABLE_ALTER_MODIFY";
        case OperationType::TABLE_ALTER_RENAME: return "TABLE_ALTER_RENAME";
        case OperationType::INDEX_CREATE:       return "INDEX_CREATE";
        case OperationType::INDEX_DROP:         return "INDEX_DROP";
        case OperationType::DATA_INSERT:        return "DATA_INSERT";
        case OperationType::DATA_DELETE:        return "DATA_DELETE";
        case OperationType::DATA_UPDATE:        return "DATA_UPDATE";
        case OperationType::DATA_SELECT:        return "DATA_SELECT";
        case OperationType::SYSTEM_START:       return "SYSTEM_START";
        case OperationType::SYSTEM_QUIT:        return "SYSTEM_QUIT";
        case OperationType::SYSTEM_ERROR:       return "SYSTEM_ERROR";
        default:                                return "UNKNOWN";
    }
}

void Logger::write_log(const LogEntry& entry)
{
    std::lock_guard<std::mutex> lock(log_mutex);
    ensure_initialized();
    
    if (!log_file.is_open()) return;
    
    // 写入分隔线
    log_file << "================================================================================" << std::endl;
    
    // 写入头部 [时间] [级别] [用户] 操作类型
    log_file << "[" << entry.timestamp << "] "
             << "[" << level_to_string(entry.level) << "] "
             << "[" << entry.user << "] "
             << op_type_to_string(entry.op_type) << std::endl;
    
    log_file << "--------------------------------------------------------------------------------" << std::endl;
    
    // 写入数据库信息
    log_file << "Database: " << (entry.database.empty() ? "-" : entry.database) << std::endl;
    
    // 写入表信息（如果有）
    if (!entry.table.empty()) {
        log_file << "Table: " << entry.table << std::endl;
    }
    
    // 写入 SQL 命令（如果有）
    if (!entry.sql_command.empty()) {
        log_file << "SQL: " << entry.sql_command << std::endl;
    }
    
    // 写入状态
    log_file << "Status: " << (entry.success ? "SUCCESS" : "FAILED") << std::endl;
    
    // 写入影响行数（如果适用）
    if (entry.affected_rows >= 0) {
        log_file << "Affected Rows: " << entry.affected_rows << std::endl;
    }
    
    // 写入附加消息（如果有）
    if (!entry.message.empty()) {
        if (entry.success) {
            log_file << "Message: " << entry.message << std::endl;
        } else {
            log_file << "Error: " << entry.message << std::endl;
        }
    }
    
    log_file << "================================================================================" << std::endl;
    log_file << std::endl;
    log_file.flush();
    
    // 控制台输出（如果启用）
    if (console_output) {
        std::cout << "[" << entry.timestamp << "] "
                  << "[" << level_to_string(entry.level) << "] "
                  << "[" << entry.user << "] "
                  << op_type_to_string(entry.op_type);
        if (!entry.sql_command.empty()) {
            std::cout << " | " << entry.sql_command;
        }
        std::cout << " | " << (entry.success ? "SUCCESS" : "FAILED");
        if (entry.affected_rows >= 0) {
            std::cout << " | " << entry.affected_rows << " row(s)";
        }
        std::cout << std::endl;
    }
}

void Logger::write_error_log(const LogEntry& entry)
{
    std::lock_guard<std::mutex> lock(log_mutex);
    ensure_initialized();
    
    if (!error_log_file.is_open()) return;
    
    error_log_file << "================================================================================" << std::endl;
    error_log_file << "[" << entry.timestamp << "] "
                   << "[" << level_to_string(entry.level) << "] "
                   << "[" << entry.user << "]" << std::endl;
    error_log_file << "--------------------------------------------------------------------------------" << std::endl;
    
    error_log_file << "Operation: " << op_type_to_string(entry.op_type) << std::endl;
    error_log_file << "Database: " << (entry.database.empty() ? "-" : entry.database) << std::endl;
    
    if (!entry.table.empty()) {
        error_log_file << "Table: " << entry.table << std::endl;
    }
    
    if (!entry.sql_command.empty()) {
        error_log_file << "SQL: " << entry.sql_command << std::endl;
    }
    
    error_log_file << "Error Message: " << entry.message << std::endl;
    error_log_file << "================================================================================" << std::endl;
    error_log_file << std::endl;
    error_log_file.flush();
}

// 配置方法
void Logger::set_log_file(const std::string& path)
{
    std::lock_guard<std::mutex> lock(log_mutex);
    if (log_file.is_open()) {
        log_file.close();
    }
    log_file_path = path;
    log_file.open(path, std::ios::app);
}

void Logger::set_error_log_file(const std::string& path)
{
    std::lock_guard<std::mutex> lock(log_mutex);
    if (error_log_file.is_open()) {
        error_log_file.close();
    }
    error_log_file_path = path;
    error_log_file.open(path, std::ios::app);
}

void Logger::set_min_level(LogLevel level)
{
    min_level = level;
}

void Logger::set_console_output(bool enabled)
{
    console_output = enabled;
}

// ========== 用户/权限系统接口预留 - 开始 ==========
// 设置当前操作用户
// 当前默认用户为 "admin"，实现用户认证系统后，在用户登录时调用此方法
// 使用示例:
//   // 用户登录成功后
//   if (auth_system.login(username, password)) {
//       Logger::get_instance()->set_current_user(username);
//   }
//   // 用户登出时
//   Logger::get_instance()->set_current_user("anonymous");
void Logger::set_current_user(const std::string& user)
{
    current_user = user;
}

std::string Logger::get_current_user() const
{
    return current_user;
}
// ========== 用户/权限系统接口预留 - 结束 ==========

void Logger::set_current_database(const std::string& db)
{
    current_database = db;
}

std::string Logger::get_current_database() const
{
    return current_database;
}

// 核心日志方法
void Logger::log(LogLevel level, OperationType op_type,
                 const std::string& sql_command,
                 bool success,
                 const std::string& message,
                 const std::string& table,
                 int affected_rows)
{
    if (level < min_level) return;
    
    LogEntry entry;
    entry.timestamp = get_timestamp();
    entry.user = current_user;
    entry.level = level;
    entry.op_type = op_type;
    entry.database = current_database;
    entry.table = table;
    entry.sql_command = sql_command;
    entry.success = success;
    entry.message = message;
    entry.affected_rows = affected_rows;
    
    write_log(entry);
    
    // 错误级别以上的也写入错误日志
    if (level >= LogLevel::ERROR) {
        write_error_log(entry);
    }
}

// 便捷方法
void Logger::log_debug(const std::string& message)
{
    log(LogLevel::DEBUG, OperationType::UNKNOWN, "", true, message);
}

void Logger::log_info(OperationType op_type, const std::string& sql_command,
                      bool success, const std::string& message)
{
    log(LogLevel::INFO, op_type, sql_command, success, message);
}

void Logger::log_warning(const std::string& message)
{
    log(LogLevel::WARNING, OperationType::UNKNOWN, "", true, message);
}

void Logger::log_error(OperationType op_type, const std::string& sql_command,
                       const std::string& error_message)
{
    log(LogLevel::ERROR, op_type, sql_command, false, error_message);
}

void Logger::log_fatal(const std::string& message)
{
    log(LogLevel::FATAL, OperationType::SYSTEM_ERROR, "", false, message);
}

// 特化的日志方法
void Logger::log_database_op(OperationType op, const char* db_name, bool success,
                             const std::string& message)
{
    std::string sql;
    switch (op) {
        case OperationType::DB_CREATE:
            sql = format_create_db_sql(db_name);
            break;
        case OperationType::DB_DROP:
            sql = format_drop_db_sql(db_name);
            break;
        case OperationType::DB_USE:
            sql = format_use_db_sql(db_name);
            if (success) {
                set_current_database(db_name);
            }
            break;
        case OperationType::DB_SHOW:
            sql = format_show_db_sql(db_name);
            break;
        default:
            sql = std::string("DATABASE OPERATION ON ") + db_name;
    }
    
    log(success ? LogLevel::INFO : LogLevel::ERROR, op, sql, success, message);
}

void Logger::log_table_op(OperationType op, const char* table_name, bool success,
                          const std::string& message)
{
    std::string sql;
    switch (op) {
        case OperationType::TABLE_CREATE:
            sql = format_create_table_sql(table_name);
            break;
        case OperationType::TABLE_DROP:
            sql = format_drop_table_sql(table_name);
            break;
        case OperationType::TABLE_SHOW:
            sql = format_show_table_sql(table_name);
            break;
        default:
            sql = std::string("TABLE OPERATION ON ") + table_name;
    }
    
    log(success ? LogLevel::INFO : LogLevel::ERROR, op, sql, success, message, table_name);
}

void Logger::log_data_op(OperationType op, const char* table_name,
                         const std::string& sql_preview, bool success,
                         int affected_rows, const std::string& message)
{
    log(success ? LogLevel::INFO : LogLevel::ERROR, op, sql_preview, success,
        message, table_name, affected_rows);
}

// 异常捕获日志
void Logger::log_exception(const char* location, const char* exception_msg)
{
    std::string message = std::string("Exception at ") + location + ": " + exception_msg;
    
    LogEntry entry;
    entry.timestamp = get_timestamp();
    entry.user = current_user;
    entry.level = LogLevel::ERROR;
    entry.op_type = OperationType::SYSTEM_ERROR;
    entry.database = current_database;
    entry.sql_command = "";
    entry.success = false;
    entry.message = message;
    entry.affected_rows = -1;
    
    write_log(entry);
    write_error_log(entry);
}

void Logger::log_exception(const char* location, const std::exception& e)
{
    log_exception(location, e.what());
}

// SQL 格式化辅助方法
std::string Logger::format_create_db_sql(const char* db_name)
{
    return std::string("CREATE DATABASE ") + db_name + ";";
}

std::string Logger::format_drop_db_sql(const char* db_name)
{
    return std::string("DROP DATABASE ") + db_name + ";";
}

std::string Logger::format_use_db_sql(const char* db_name)
{
    return std::string("USE ") + db_name + ";";
}

std::string Logger::format_show_db_sql(const char* db_name)
{
    return std::string("SHOW DATABASE ") + db_name + ";";
}

std::string Logger::format_create_table_sql(const char* table_name)
{
    return std::string("CREATE TABLE ") + table_name + " (...);";
}

std::string Logger::format_drop_table_sql(const char* table_name)
{
    return std::string("DROP TABLE ") + table_name + ";";
}

std::string Logger::format_show_table_sql(const char* table_name)
{
    return std::string("SHOW TABLE ") + table_name + ";";
}

std::string Logger::format_rename_table_sql(const char* old_name, const char* new_name)
{
    return std::string("RENAME TABLE ") + old_name + " TO " + new_name + ";";
}

std::string Logger::format_alter_add_sql(const char* table_name, const char* col_name)
{
    return std::string("ALTER TABLE ") + table_name + " ADD COLUMN " + col_name + " ...;";
}

std::string Logger::format_alter_drop_sql(const char* table_name, const char* col_name)
{
    return std::string("ALTER TABLE ") + table_name + " DROP COLUMN " + col_name + ";";
}

std::string Logger::format_alter_modify_sql(const char* table_name, const char* col_name)
{
    return std::string("ALTER TABLE ") + table_name + " MODIFY COLUMN " + col_name + " ...;";
}

std::string Logger::format_alter_rename_sql(const char* table_name, const char* old_col, const char* new_col)
{
    return std::string("ALTER TABLE ") + table_name + " RENAME COLUMN " + old_col + " TO " + new_col + ";";
}

std::string Logger::format_insert_sql(const char* table_name, int row_count)
{
    std::ostringstream oss;
    oss << "INSERT INTO " << table_name << " VALUES (...); -- " << row_count << " row(s)";
    return oss.str();
}

std::string Logger::format_delete_sql(const char* table_name)
{
    return std::string("DELETE FROM ") + table_name + " WHERE ...;";
}

std::string Logger::format_update_sql(const char* table_name, const char* col_name)
{
    return std::string("UPDATE ") + table_name + " SET " + col_name + " = ... WHERE ...;";
}

std::string Logger::format_select_sql(const char* table_name)
{
    return std::string("SELECT ... FROM ") + table_name + " WHERE ...;";
}

std::string Logger::format_create_index_sql(const char* table_name, const char* col_name)
{
    return std::string("CREATE INDEX ON ") + table_name + "(" + col_name + ");";
}

std::string Logger::format_drop_index_sql(const char* table_name, const char* col_name)
{
    return std::string("DROP INDEX ON ") + table_name + "(" + col_name + ");";
}

#ifndef KOMB_API_H
#define KOMB_API_H

#include <pthread.h>
#include <stdint.h>
#include "kombmtx.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief 创建komb互斥锁
 * @param mutex 指向komb_mutex_t的指针
 * @return 成功返回0，失败返回错误码
 */
komb_mutex_t* komb_api_mutex_create(pthread_mutexattr_t *attr);

/**
 * @brief 销毁komb互斥锁
 * @param mutex 指向komb_mutex_t的指针
 * @return 成功返回0，失败返回错误码
 */
int komb_api_mutex_destroy(komb_mutex_t *mutex);

/**
 * @brief 获取komb互斥锁
 * @param mutex 指向komb_mutex_t的指针
 * @return 成功返回0，失败返回错误码
 */
int komb_api_mutex_lock(komb_mutex_t *mutex);

/**
 * @brief 尝试获取komb互斥锁
 * @param mutex 指向komb_mutex_t的指针
 * @return 成功返回0，失败返回错误码
 */
int komb_api_mutex_trylock(komb_mutex_t *mutex);

/**
 * @brief 释放komb互斥锁
 * @param mutex 指向komb_mutex_t的指针
 * @return 成功返回0，失败返回错误码
 */
void komb_api_mutex_unlock(komb_mutex_t *mutex);

/**
 * @brief 初始化komb条件变量
 * @param cond 指向komb_cond_t的指针
 * @param attr 指向pthread_condattr_t的指针
 * @return 成功返回0，失败返回错误码
 */
int komb_api_cond_init(komb_cond_t *cond, const pthread_condattr_t *attr);

/**
 * @brief 等待komb条件变量
 * @param cond 指向komb_cond_t的指针
 * @param mutex 指向komb_mutex_t的指针
 * @return 成功返回0，失败返回错误码
 */
int komb_api_cond_wait(komb_cond_t *cond, komb_mutex_t *mutex);

/**
 * @brief 唤醒一个等待komb条件变量的线程
 * @param cond 指向komb_cond_t的指针
 * @return 成功返回0，失败返回错误码
 */
int komb_api_cond_signal(komb_cond_t *cond);

/**
 * @brief 唤醒所有等待komb条件变量的线程
 * @param cond 指向komb_cond_t的指针
 * @return 成功返回0，失败返回错误码
 */
int komb_api_cond_broadcast(komb_cond_t *cond);

/**
 * @brief 销毁komb条件变量
 * @param cond 指向komb_cond_t的指针
 * @return 成功返回0，失败返回错误码
 */
int komb_api_cond_destroy(komb_cond_t *cond);

/**
 * @brief 初始化线程上下文，必须在每个使用komb锁的线程开始时调用
 */
void komb_api_thread_start(void);

/**
 * @brief 清理线程上下文，建议在每个使用komb锁的线程结束时调用
 */
void komb_api_thread_exit(void);

/**
 * @brief 获取当前活动线程的数量
 * @return 当前活动线程的数量
 */
unsigned int komb_api_get_active_threads_count(void);

#ifdef __cplusplus
}
#endif

#endif /* KOMB_API_H */ 
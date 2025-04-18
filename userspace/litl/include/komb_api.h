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
 * @brief 初始化线程上下文，必须在每个使用komb锁的线程开始时调用
 */
void komb_api_thread_start(void);

/**
 * @brief 清理线程上下文，建议在每个使用komb锁的线程结束时调用
 */
void komb_api_thread_exit(void);

#ifdef __cplusplus
}
#endif

#endif /* KOMB_API_H */ 
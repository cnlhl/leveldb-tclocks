// Copyright (c) 2011 The LevelDB Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file. See the AUTHORS file for names of contributors.

#include "port/port_posix.h"

#include <cstdlib>
#include <stdio.h>
#include <string.h>
#include <time.h>


namespace leveldb {
namespace port {

#if defined(USE_TCLOCK) && defined(LEVELDB_TESTS)
std::atomic<int> Mutex::test_switch_to_tclock_count_{0};
std::atomic<int> Mutex::test_switch_to_pthread_count_{0};
#endif

static void PthreadCall(const char* label, int result) {
  if (result != 0) {
    fprintf(stderr, "pthread %s: %s\n", label, strerror(result));
    abort();
  }
}

#ifdef USE_TCLOCK
static pthread_once_t komb_tls_once = PTHREAD_ONCE_INIT;
static pthread_key_t komb_tls_key;

static void KombTlsDestructor(void* value) {
  if (value != nullptr) {
    komb_api_thread_exit();
  }
}

static void InitKombTlsKey() {
  PthreadCall("create key", pthread_key_create(&komb_tls_key, KombTlsDestructor));
}

static void EnsureTLSReady() {
  static thread_local bool ready = false;
  if (!ready) {
    PthreadCall("once", pthread_once(&komb_tls_once, InitKombTlsKey));
    komb_api_thread_start();
    ready = true;
    PthreadCall("set specific", pthread_setspecific(komb_tls_key, reinterpret_cast<void*>(1)));
  }
}
#endif

Mutex::Mutex() {
  PthreadCall("init mutex", pthread_mutex_init(&pm_, NULL));
#ifdef USE_TCLOCK
  km_ = komb_api_mutex_create(NULL);
  backend_.store(Backend::PTHREAD, std::memory_order_release);
  window_start_ns_.store(0, std::memory_order_release);
  fail_cnt_.store(0, std::memory_order_release);
  consecutive_fail_windows_cnt_.store(0, std::memory_order_release);
  success_window_start_ns_. store(0, std::memory_order_release);
  success_cnt_.store(0, std::memory_order_release);
  consecutive_success_windows_cnt_.store(0, std::memory_order_release);
#endif
#if defined(LEVELDB_TESTS) && defined(USE_TCLOCK) 
  Test_ResetSwitchCounters();
#endif
}

Mutex::~Mutex() {
  PthreadCall("destroy mutex", pthread_mutex_destroy(&pm_));
#ifdef USE_TCLOCK
  if (km_ != nullptr) {
    komb_api_mutex_destroy(km_);
  }
#endif
}

void Mutex::Lock() {
#ifdef USE_TCLOCK
  // 确保TLS准备就绪
  EnsureTLSReady();
  while(true){
    Backend b = backend_.load(std::memory_order_acquire);
    struct timespec now;
    clock_gettime(CLOCK_MONOTONIC, &now);
    int64_t now_ns = now.tv_sec * 1000000000LL + now.tv_nsec;

    if (b == Backend::PTHREAD) {
      if (pthread_mutex_trylock(&pm_) == 0) {
        if(backend_.load(std::memory_order_acquire) == Backend::PTHREAD){
          return;
        }
        pthread_mutex_unlock(&pm_);
        continue;
      } else {
        int64_t current_window_start = window_start_ns_.load(std::memory_order_acquire);
        bool initiate_switch = false;
        // 获取 pm_ 锁失败，进入失败路径，只在失败路径下走窗口统计逻辑
        if (now_ns - current_window_start > kWindowNs) {

          if(window_start_ns_.compare_exchange_strong(current_window_start, now_ns, std::memory_order_acq_rel)) {
            int64_t finished_window_fail_cnt = fail_cnt_.exchange(0, std::memory_order_acq_rel);
            if(finished_window_fail_cnt >= kThreshold) {
              int current_fail_windows_cnt = consecutive_fail_windows_cnt_.fetch_add(1, std::memory_order_acq_rel);
              if(current_fail_windows_cnt >= consecutive_fail_windows_threshold){
                initiate_switch = true;
                consecutive_fail_windows_cnt_.store(0, std::memory_order_release);
              }
            }else{
              consecutive_fail_windows_cnt_.store(0, std::memory_order_release);
            }
            // 成功更新窗口起始时间
          }
        }
        fail_cnt_.fetch_add(1, std::memory_order_relaxed);
        // printf("fail_cnt_ = %ld\n", fail_cnt_.load());
        
        if (initiate_switch) {
          PthreadCall("lock", pthread_mutex_lock(&pm_));
          Backend expected = Backend::PTHREAD;
          if (!backend_.compare_exchange_strong(expected, Backend::SWITCHING_TO_TCLOCK,
                                               std::memory_order_acq_rel)) {
            // 如果状态已经不是 PTHREAD，说明其他线程正在切换，释放 pm_ 并重试
            pthread_mutex_unlock(&pm_);
            continue;
          }
          
          // 现在持有 pm_ 锁，并且状态是 SWITCHING_TO_TCLOCK
          // 先获取 km_ 锁
          komb_api_mutex_lock(km_);
          
          // 将状态切换到 TCLOCK
          backend_.store(Backend::TCLOCK, std::memory_order_release);
#ifdef LEVELDB_TESTS
          test_switch_to_tclock_count_.fetch_add(1, std::memory_order_relaxed);
#endif
          printf("Switching to TCLOCK\n");
          
          // 释放 pm_ 锁
          pthread_mutex_unlock(&pm_);
        } else {
          PthreadCall("lock", pthread_mutex_lock(&pm_));
          if (backend_.load(std::memory_order_acquire) == Backend::PTHREAD) {
            return;
          }
          pthread_mutex_unlock(&pm_);
          continue;
        }
      }
      return;
    }else if (b == Backend::TCLOCK) {
      unsigned int active_komb_threads = komb_api_get_active_threads_count();
      bool force_switch = (active_komb_threads < kForcePthreadActiveThreadThreshold);

      // if (force_switch) {
      //   Backend expected = Backend::TCLOCK;
      //   if (backend_.compare_exchange_strong(expected, Backend::SWITCHING_TO_PTHREAD, std::memory_order_acq_rel)) {
      //       printf("Switching to PTHREAD (forced by low active_komb_threads: %u)\n", active_komb_threads);
      //       consecutive_success_windows_cnt_.store(0, std::memory_order_release);
      //       success_cnt_.store(0, std::memory_order_release);
      //       continue;
      //   } else {
      //       continue;
      //   }
      // }

      if (komb_api_mutex_trylock(km_) == 0) {
        if(backend_.load(std::memory_order_acquire) == Backend::TCLOCK){
          int64_t current_window_start = success_window_start_ns_.load(std::memory_order_acquire);
          bool initiate_back_switch = false;
          if(now_ns - current_window_start > kBackWindowNs){
            if(success_window_start_ns_.compare_exchange_strong(current_window_start, now_ns, std::memory_order_acq_rel)){
              int64_t finished_window_success_cnt = success_cnt_.exchange(0, std::memory_order_acq_rel);
              if(finished_window_success_cnt >= kBackToThreadThreshold){
                int current_success_windows_cnt = consecutive_success_windows_cnt_.fetch_add(1, std::memory_order_acq_rel);
                if(current_success_windows_cnt >= consecutive_success_windows_threshold){
                  initiate_back_switch = true;
                  consecutive_success_windows_cnt_.store(0, std::memory_order_release);
                }
              }else{
                consecutive_success_windows_cnt_.store(0, std::memory_order_release);
              }
            }
          }
          success_cnt_.fetch_add(1, std::memory_order_relaxed);
          if(initiate_back_switch){
            Backend expected = Backend::TCLOCK;
            if (backend_.compare_exchange_strong(expected, Backend::SWITCHING_TO_PTHREAD, std::memory_order_acq_rel)) {
              printf("start switching to PTHREAD\n"); 
            }
          }
          return;
        }else{
          komb_api_mutex_unlock(km_);
          continue;
        }
      }else{
        komb_api_mutex_lock(km_);
        if(backend_.load(std::memory_order_acquire) == Backend::TCLOCK){
          // 核对锁类型正确
          return;
        }else{
          komb_api_mutex_unlock(km_);
          continue;
        }
      }
    }else if (b == Backend::SWITCHING_TO_PTHREAD) {
      PthreadCall("lock", pthread_mutex_lock(&pm_));
      if (backend_.load(std::memory_order_acquire) == Backend::SWITCHING_TO_PTHREAD) {
        while(komb_api_mutex_trylock(km_) != 0){
          // 等待 km_ 锁释放
          std::this_thread::yield();
        }
        backend_.store(Backend::PTHREAD, std::memory_order_release);
        printf("Switching to PTHREAD\n");
#ifdef LEVELDB_TESTS
        test_switch_to_pthread_count_.fetch_add(1, std::memory_order_relaxed);
#endif
        // 释放 km_ 锁
        komb_api_mutex_unlock(km_);
        return;
      }
      pthread_mutex_unlock(&pm_);
      continue;
    }else if(b == Backend::SWITCHING_TO_TCLOCK) {
      std::this_thread::yield();
      continue;
    }
  }
#else
  PthreadCall("lock", pthread_mutex_lock(&pm_));
#endif
}

void Mutex::Unlock() {
#ifdef USE_TCLOCK
  Backend current = backend_.load(std::memory_order_acquire);
  if (current == Backend::PTHREAD) {
    PthreadCall("unlock", pthread_mutex_unlock(&pm_));
  } else if (current == Backend::TCLOCK ||current == Backend::SWITCHING_TO_PTHREAD) {
    // 确保TLS准备就绪
    EnsureTLSReady();
    komb_api_mutex_unlock(km_);
  }

#else
  PthreadCall("unlock", pthread_mutex_unlock(&pm_));
#endif
}

bool Mutex::TryLock() {
#ifdef USE_TCLOCK
  while(true){
    Backend current = backend_.load(std::memory_order_acquire);
    struct timespec now;
    clock_gettime(CLOCK_MONOTONIC, &now);
    int64_t now_ns = now.tv_sec * 1000000000LL + now.tv_nsec;
      
    if (current == Backend::PTHREAD) {
      if (now_ns - window_start_ns_ > kWindowNs) {
        window_start_ns_ = now_ns;
        fail_cnt_ = 0;
      }
      if (pthread_mutex_trylock(&pm_) == 0) {
        if(backend_.load(std::memory_order_acquire) == Backend::PTHREAD){
          // 核对锁类型正确
          return true;
        }
        pthread_mutex_unlock(&pm_);
        continue;
      }
      fail_cnt_++;
      return false;
    } else if (current == Backend::TCLOCK) {
      // 确保TLS准备就绪
      EnsureTLSReady();
      if (komb_api_mutex_trylock(km_) == 0) {
        if(backend_.load(std::memory_order_acquire) == Backend::TCLOCK){
          if(now_ns - success_window_start_ns_ > kBackWindowNs){
            success_window_start_ns_ = now_ns;
            success_cnt_ = 0;
          }
          success_cnt_++;
          return true;
        }
        komb_api_mutex_unlock(km_);
        continue;
      }
      return false;
    }
    // 两个方向的切换中间态都涉及忙等某个锁，有悖trylock的逻辑初衷，故直接返回失败
    return false;
  }
#else
  return pthread_mutex_trylock(&pm_) == 0;
#endif
}

CondVar::CondVar(Mutex* mu)
    : mu_(mu) {
#ifdef USE_TCLOCK
    PthreadCall("init cv", komb_api_cond_init(&kcv_, NULL));
#else
    PthreadCall("init cv", pthread_cond_init(&cv_, NULL));
#endif
}

CondVar::~CondVar() { 
#ifdef USE_TCLOCK
    PthreadCall("destroy cv", komb_api_cond_destroy(&kcv_));
#else
    PthreadCall("destroy cv", pthread_cond_destroy(&cv_));
#endif
}

void CondVar::Wait() {
#ifdef USE_TCLOCK
  Mutex::Backend current = mu_->backend_.load(std::memory_order_acquire);
  if (current == Mutex::Backend::TCLOCK) {
    // 确保TLS准备就绪
    EnsureTLSReady();
    PthreadCall("wait", komb_api_cond_wait(&kcv_, mu_->km_));
  } else if (current == Mutex::Backend::PTHREAD) {
    PthreadCall("wait", pthread_cond_wait(&cv_, &mu_->pm_));
  }
  // 忽略 SWITCHING_TO_TCLOCK 状态，因为此时锁的持有者一定是正在切换的线程
#else
  PthreadCall("wait", pthread_cond_wait(&cv_, &mu_->pm_));
#endif
}

void CondVar::Signal() {
#ifdef USE_TCLOCK
  Mutex::Backend current = mu_->backend_.load(std::memory_order_acquire);
  if (current == Mutex::Backend::TCLOCK) {
    // 确保TLS准备就绪
    EnsureTLSReady();
    PthreadCall("signal", komb_api_cond_signal(&kcv_));
  } else if (current == Mutex::Backend::PTHREAD) {
    PthreadCall("signal", pthread_cond_signal(&cv_));
  }
  // 忽略 SWITCHING_TO_TCLOCK 状态，因为此时锁的持有者一定是正在切换的线程
#else
  PthreadCall("signal", pthread_cond_signal(&cv_));
#endif
}

void CondVar::SignalAll() {
#ifdef USE_TCLOCK
  Mutex::Backend current = mu_->backend_.load(std::memory_order_acquire);
  if (current == Mutex::Backend::TCLOCK) {
    // 确保TLS准备就绪
    EnsureTLSReady();
    PthreadCall("broadcast", komb_api_cond_broadcast(&kcv_));
  } else if (current == Mutex::Backend::PTHREAD) {
    PthreadCall("broadcast", pthread_cond_broadcast(&cv_));
  }
  // 忽略 SWITCHING_TO_TCLOCK 状态，因为此时锁的持有者一定是正在切换的线程
#else
  PthreadCall("broadcast", pthread_cond_broadcast(&cv_));
#endif
}

void InitOnce(OnceType* once, void (*initializer)()) {
  PthreadCall("once", pthread_once(once, initializer));
}

}  // namespace port
}  // namespace leveldb

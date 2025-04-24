// Copyright (c) 2011 The LevelDB Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file. See the AUTHORS file for names of contributors.

#include "port/port_posix.h"

#include <cstdlib>
#include <stdio.h>
#include <string.h>
#include <time.h>

#ifdef USE_TCLOCK
static pthread_once_t komb_tls_once = PTHREAD_ONCE_INIT;
static pthread_key_t komb_tls_key;
static thread_local bool komb_tls_ready = false;

static void KombTlsDestructor(void* value) {
  if (value != nullptr) {
    komb_api_thread_exit();
  }
}

static void InitKombTlsKey() {
  PthreadCall("create key", pthread_key_create(&komb_tls_key, KombTlsDestructor));
}
#endif

namespace leveldb {
namespace port {

static void PthreadCall(const char* label, int result) {
  if (result != 0) {
    fprintf(stderr, "pthread %s: %s\n", label, strerror(result));
    abort();
  }
}

Mutex::Mutex() : backend_(Backend::PTHREAD) {
  PthreadCall("init mutex", pthread_mutex_init(&pm_, NULL));
#ifdef USE_TCLOCK
  km_ = nullptr;
  window_start_ns_ = 0;
  fail_cnt_ = 0;
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
  if (backend_ == Backend::PTHREAD) {
    struct timespec now;
    clock_gettime(CLOCK_MONOTONIC, &now);
    int64_t now_ns = now.tv_sec * 1000000000LL + now.tv_nsec;
    
    if (now_ns - window_start_ns_ > kWindowNs) {
      window_start_ns_ = now_ns;
      fail_cnt_ = 0;
    }
    
    if (pthread_mutex_trylock(&pm_) == 0) {
      return;
    }
    
    fail_cnt_++;
    
    if (fail_cnt_ >= kThreshold) {
      if (km_ == nullptr) {
        km_ = komb_api_mutex_create(nullptr);
        if (km_ == nullptr) {
          // Failed to create TCLock mutex, stay with pthread
          backend_ = Backend::PTHREAD;
          PthreadCall("lock", pthread_mutex_lock(&pm_));
          return;
        }
      }
      
      // Wait for current holder to release
      while (pthread_mutex_trylock(&pm_) != 0) {
        // TODO(safety): Handle thread cancellation
      }
      pthread_mutex_unlock(&pm_);
      
      backend_ = Backend::TCLOCK;
      
      if (!komb_tls_ready) {
        PthreadCall("once", pthread_once(&komb_tls_once, InitKombTlsKey));
        komb_api_thread_start();
        komb_tls_ready = true;
        PthreadCall("set specific", pthread_setspecific(komb_tls_key, reinterpret_cast<void*>(1)));
      }
    } else {
      PthreadCall("lock", pthread_mutex_lock(&pm_));
    }
  } else {
    komb_api_mutex_lock(km_);
  }
#else
  PthreadCall("lock", pthread_mutex_lock(&pm_));
#endif
}

void Mutex::Unlock() {
#ifdef USE_TCLOCK
  if (backend_ == Backend::PTHREAD) {
    PthreadCall("unlock", pthread_mutex_unlock(&pm_));
  } else {
    komb_api_mutex_unlock(km_);
  }
#else
  PthreadCall("unlock", pthread_mutex_unlock(&pm_));
#endif
}

bool Mutex::TryLock() {
#ifdef USE_TCLOCK
  if (backend_ == Backend::PTHREAD) {
    struct timespec now;
    clock_gettime(CLOCK_MONOTONIC, &now);
    int64_t now_ns = now.tv_sec * 1000000000LL + now.tv_nsec;
    
    if (now_ns - window_start_ns_ > kWindowNs) {
      window_start_ns_ = now_ns;
      fail_cnt_ = 0;
    }
    
    if (pthread_mutex_trylock(&pm_) == 0) {
      return true;
    }
    
    fail_cnt_++;
    return false;
  } else {
    return komb_api_mutex_trylock(km_) == 0;
  }
#else
  return pthread_mutex_trylock(&pm_) == 0;
#endif
}

CondVar::CondVar(Mutex* mu)
    : mu_(mu) {
    PthreadCall("init cv", pthread_cond_init(&cv_, NULL));
}

CondVar::~CondVar() { PthreadCall("destroy cv", pthread_cond_destroy(&cv_)); }

void CondVar::Wait() {
  PthreadCall("wait", pthread_cond_wait(&cv_, &mu_->pm_));
}

void CondVar::Signal() {
  PthreadCall("signal", pthread_cond_signal(&cv_));
}

void CondVar::SignalAll() {
  PthreadCall("broadcast", pthread_cond_broadcast(&cv_));
}

void InitOnce(OnceType* once, void (*initializer)()) {
  PthreadCall("once", pthread_once(once, initializer));
}

}  // namespace port
}  // namespace leveldb

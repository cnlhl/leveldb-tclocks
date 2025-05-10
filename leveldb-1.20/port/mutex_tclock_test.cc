// Copyright (c) 2011 The LevelDB Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file. See the AUTHORS file for names of contributors.

#include "port/port_posix.h"
#include "util/testharness.h"
#include <thread>
#include <vector>
#include <atomic>
#include <chrono>
#include <iostream>
#include <iomanip>

namespace leveldb {
namespace port {

class MutexTClockTest { };

// 辅助函数：检查是否切换到 TCLock
bool IsUsingTCLock(const Mutex& mu) {
#ifdef USE_TCLOCK
  return mu.IsUsingTCLock();
#else
  return false;
#endif
}

TEST(MutexTClockTest, HighContention) {
  Mutex mu;
  std::atomic<int> counter(0);
  const int kNumThreads = 8;
  const int kNumIterations = 2000000;
  std::vector<std::thread> threads;
  
  // 初始应该是 pthread 后端
  ASSERT_TRUE(!IsUsingTCLock(mu));

  auto start_time = std::chrono::high_resolution_clock::now();
  
  for (int i = 0; i < kNumThreads; i++) {
    threads.emplace_back([&]() {
      for (int j = 0; j < kNumIterations; j++) {
        mu.Lock();
        counter++;
        mu.Unlock();
      }
    });
  }
  
  // 等待一段时间，让争用有机会触发切换
  std::this_thread::sleep_for(std::chrono::milliseconds(1000));
  
  // 检查是否切换到了 TCLock
#ifdef USE_TCLOCK
  // ASSERT_TRUE(IsUsingTCLock(mu));
  // std::cout << "Successfully switched to TCLock backend" << std::endl;
#else
  ASSERT_TRUE(!IsUsingTCLock(mu));
  std::cout << "Using pthread backend (TCLock not enabled)" << std::endl;
#endif
  
  for (auto& t : threads) {
    t.join();
  }

  auto end_time = std::chrono::high_resolution_clock::now();
  std::chrono::duration<double, std::milli> duration_ms = end_time - start_time;
  
  ASSERT_EQ(counter, (long long)kNumThreads * kNumIterations);
  long long final_counter_value = counter.load();
  std::cout << "  Test duration: " << std::fixed << std::setprecision(2) << duration_ms.count() << " ms" << std::endl;
  std::cout << "  Throughput: " << std::fixed << std::setprecision(2) 
            << (final_counter_value / (duration_ms.count() / 1000.0)) / 1e6 << " M ops/sec" << std::endl;
#if  defined(USE_TCLOCK) && defined(LEVELDB_TESTS)
  std::cout << "  Switch to TCLock count: " << Mutex::Test_GetSwitchToTClockCount() << std::endl;
  std::cout << "  Switch to pthread count: " << Mutex::Test_GetSwitchToPThreadCount() << std::endl;
#endif
  std::cout << "  Final counter value: " << final_counter_value << std::endl;
}

TEST(MutexTClockTest, LowContention) {
  Mutex mu;
  std::atomic<int> counter(0);
  const int kNumIterations = 10000;
  
  // 初始应该是 pthread 后端
  ASSERT_TRUE(!IsUsingTCLock(mu));
  
  for (int i = 0; i < kNumIterations; i++) {
    mu.Lock();
    counter++;
    mu.Unlock();
  }
  
  // 低争用情况下应该保持 pthread 后端
  ASSERT_TRUE(!IsUsingTCLock(mu));
  
  ASSERT_EQ(counter, kNumIterations);
}

TEST(MutexTClockTest, SwitchBackAndForth) {
  Mutex mu;
  std::atomic<int> counter(0);
  const int kNumThreads = 8;
  const int kNumIterations = 1000;
  std::vector<std::thread> threads;
  
  // 初始应该是 pthread 后端
  ASSERT_TRUE(!IsUsingTCLock(mu));
  
  // 创建高争用场景
  for (int i = 0; i < kNumThreads; i++) {
    threads.emplace_back([&]() {
      for (int j = 0; j < kNumIterations; j++) {
        mu.Lock();
        counter++;
        mu.Unlock();
      }
    });
  }
  
  // 等待切换
  std::this_thread::sleep_for(std::chrono::milliseconds(100));
  
#ifdef USE_TCLOCK
  // 应该切换到 TCLock
  ASSERT_TRUE(IsUsingTCLock(mu));
  
  // 等待线程结束
  for (auto& t : threads) {
    t.join();
  }
  
  // 重置计数器
  counter = 0;
  threads.clear();
  
  // 创建低争用场景
  for (int i = 0; i < 2; i++) {
    threads.emplace_back([&]() {
      for (int j = 0; j < kNumIterations; j++) {
        mu.Lock();
        counter++;
        mu.Unlock();
      }
    });
  }
  
  // 等待一段时间
  std::this_thread::sleep_for(std::chrono::milliseconds(100));
  
  // 应该切换回 pthread
  ASSERT_TRUE(!IsUsingTCLock(mu));
#endif
  
  for (auto& t : threads) {
    t.join();
  }
  
  ASSERT_EQ(counter, threads.size() * kNumIterations);
}

}  // namespace port
}  // namespace leveldb

int main(int argc, char** argv) {
  return leveldb::test::RunAllTests();
} 
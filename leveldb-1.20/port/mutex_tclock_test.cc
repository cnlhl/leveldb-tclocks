// Copyright (c) 2011 The LevelDB Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file. See the AUTHORS file for names of contributors.

#include "port/port_posix.h"
#include "util/testharness.h"
#include <thread>
#include <vector>
#include <atomic>

namespace leveldb {
namespace port {

class MutexTClockTest { };

TEST(MutexTClockTest, HighContention) {
  Mutex mu;
  std::atomic<int> counter(0);
  const int kNumThreads = 8;
  const int kNumIterations = 10000;
  std::vector<std::thread> threads;
  
  for (int i = 0; i < kNumThreads; i++) {
    threads.emplace_back([&]() {
      for (int j = 0; j < kNumIterations; j++) {
        mu.Lock();
        counter++;
        mu.Unlock();
      }
    });
  }
  
  for (auto& t : threads) {
    t.join();
  }
  
  ASSERT_EQ(counter, kNumThreads * kNumIterations);
}

TEST(MutexTClockTest, LowContention) {
  Mutex mu;
  std::atomic<int> counter(0);
  const int kNumIterations = 10000;
  
  for (int i = 0; i < kNumIterations; i++) {
    mu.Lock();
    counter++;
    mu.Unlock();
  }
  
  ASSERT_EQ(counter, kNumIterations);
}

}  // namespace port
}  // namespace leveldb

int main(int argc, char** argv) {
  return leveldb::test::RunAllTests();
} 
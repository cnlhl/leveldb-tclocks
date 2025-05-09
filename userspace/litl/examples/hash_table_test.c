#include <time.h>
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <stdint.h>

#define HASH_TABLE_SIZE 4096
#define NUM_THREADS 64
#define NUM_OPERATIONS 100000
#define INITIAL_ITEMS 500000

// 链表节点
typedef struct Node {
    int key;
    int value;
    struct Node* next;
} Node;

// 哈希表桶
typedef struct Bucket {
    Node* head;           // 链表头指针
    pthread_spinlock_t lock; // 改用自旋锁
} Bucket;

// 哈希表
typedef struct HashTable {
    Bucket buckets[HASH_TABLE_SIZE];
} HashTable;

// 初始化哈希表
void hash_table_init(HashTable* ht) {
    for (int i = 0; i < HASH_TABLE_SIZE; i++) {
        ht->buckets[i].head = NULL;
        pthread_spin_init(&ht->buckets[i].lock, 0); // 初始化自旋锁
    }
}

// 简单的哈希函数
uint32_t hash_function(int key) {
    return key % HASH_TABLE_SIZE;
}

// 插入键值对
void hash_table_insert(HashTable* ht, int key, int value) {
    uint32_t index = hash_function(key);
    Bucket* bucket = &ht->buckets[index];

    // 获取自旋锁
    pthread_spin_lock(&bucket->lock);

    // 创建新节点
    Node* new_node = (Node*)malloc(sizeof(Node));
    new_node->key = key;
    new_node->value = value;
    new_node->next = bucket->head;

    // 插入链表头部
    bucket->head = new_node;

    // 释放自旋锁
    pthread_spin_unlock(&bucket->lock);
}

// 查找键值对
int hash_table_lookup(HashTable* ht, int key) {
    uint32_t index = hash_function(key);
    Bucket* bucket = &ht->buckets[index];

    // 获取自旋锁
    pthread_spin_lock(&bucket->lock);

    // 遍历链表
    Node* current = bucket->head;
    while (current) {
        if (current->key == key) {
            int value = current->value;

            // 释放自旋锁
            pthread_spin_unlock(&bucket->lock);
            return value;
        }
        current = current->next;
    }

    // 释放自旋锁
    pthread_spin_unlock(&bucket->lock);
    return -1; // 未找到
}

// 删除键值对
void hash_table_delete(HashTable* ht, int key) {
    uint32_t index = hash_function(key);
    Bucket* bucket = &ht->buckets[index];

    // 获取自旋锁
    pthread_spin_lock(&bucket->lock);

    // 遍历链表
    Node* current = bucket->head;
    Node* prev = NULL;
    while (current) {
        if (current->key == key) {
            if (prev) {
                prev->next = current->next;
            } else {
                bucket->head = current->next;
            }
            free(current);

            // 释放自旋锁
            pthread_spin_unlock(&bucket->lock);
            return;
        }
        prev = current;
        current = current->next;
    }

    // 释放自旋锁
    pthread_spin_unlock(&bucket->lock);
}

// 销毁哈希表
void hash_table_destroy(HashTable* ht) {
    for (int i = 0; i < HASH_TABLE_SIZE; i++) {
        Bucket* bucket = &ht->buckets[i];

        // 获取自旋锁
        pthread_spin_lock(&bucket->lock);

        // 释放链表
        Node* current = bucket->head;
        while (current) {
            Node* temp = current;
            current = current->next;
            free(temp);
        }

        // 释放自旋锁
        pthread_spin_unlock(&bucket->lock);
        pthread_spin_destroy(&bucket->lock);
    }
}

HashTable ht;

// 在main函数之前添加新的初始化函数
void initialize_with_items(HashTable* ht) {
    for (int i = 0; i < INITIAL_ITEMS; i++) {
        int key = i;  // 使用连续的键以确保均匀分布
        int value = rand();
        hash_table_insert(ht, key, value);
    }
}

// 修改线程函数，让所有查找操作都访问同一个槽位
void* thread_func(void* arg) {
    int thread_id = (int)(long)arg;
    int fixed_key = INITIAL_ITEMS - 1;  // 使用固定的键，确保所有线程访问同一个槽位
    for (int i = 0; i < NUM_OPERATIONS; i++) {
        hash_table_lookup(&ht, fixed_key);
    }
    return NULL;
}

int main() {
    pthread_t threads[NUM_THREADS];
    hash_table_init(&ht);
    
    // 首先填充哈希表，确保最后一个键在目标槽位
    printf("Initializing hash table with %d items...\n", INITIAL_ITEMS);
    initialize_with_items(&ht);
    
    // 验证目标槽位的项目数量
    int target_bucket = hash_function(INITIAL_ITEMS - 1);
    int count = 0;
    Node* current = ht.buckets[target_bucket].head;
    while (current) {
        count++;
        current = current->next;
    }
    
    printf("Target bucket statistics:\n");
    printf("Bucket index: %d\n", target_bucket);
    printf("Items in target bucket: %d\n", count);

    // 记录开始时间
    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    // 创建线程
    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_create(&threads[i], NULL, thread_func, (void*)(long)i);
    }

    // 等待线程结束
    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }

    // 记录结束时间
    clock_gettime(CLOCK_MONOTONIC, &end);

    // 计算执行时间
    double elapsed = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;
    printf("Elapsed time: %.6f seconds\n", elapsed);

    // 销毁哈希表
    hash_table_destroy(&ht);
    return 0;
}
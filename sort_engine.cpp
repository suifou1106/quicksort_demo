#include <algorithm>
#include <cstdlib>
#include "pdqsort.h" // Nhúng trực tiếp thuật toán pdqsort

extern "C" {

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

    void swap_elem(int& a, int& b) {
        int temp = a; a = b; b = temp;
    }

    int partition(int* arr, int low, int high, int pivot_idx) {
        swap_elem(arr[pivot_idx], arr[high]);
        int pivot = arr[high];
        int i = low - 1;
        for (int j = low; j < high; j++) {
            if (arr[j] <= pivot) {
                i++;
                swap_elem(arr[i], arr[j]);
            }
        }
        swap_elem(arr[i + 1], arr[high]);
        return i + 1;
    }

    // Các thuật toán kinh điển
    EXPORT void qs_first(int* arr, int low, int high) {
        if (low < high) {
            int pi = partition(arr, low, high, low);
            qs_first(arr, low, pi - 1);
            qs_first(arr, pi + 1, high);
        }
    }

    EXPORT void qs_last(int* arr, int low, int high) {
        if (low < high) {
            int pi = partition(arr, low, high, high);
            qs_last(arr, low, pi - 1);
            qs_last(arr, pi + 1, high);
        }
    }

    EXPORT void qs_middle(int* arr, int low, int high) {
        if (low < high) {
            int pi = partition(arr, low, high, low + (high - low) / 2);
            qs_middle(arr, low, pi - 1);
            qs_middle(arr, pi + 1, high);
        }
    }

    EXPORT void qs_random(int* arr, int low, int high) {
        if (low < high) {
            int random_idx = low + rand() % (high - low + 1);
            int pi = partition(arr, low, high, random_idx);
            qs_random(arr, low, pi - 1);
            qs_random(arr, pi + 1, high);
        }
    }

    // pdqsort
    EXPORT void qs_pdqsort(int* arr, int low, int high) {
        // Hàm pdqsort nhận con trỏ đầu và con trỏ ngay sau phần tử cuối cùng
        pdqsort(arr + low, arr + high + 1);
    }
}

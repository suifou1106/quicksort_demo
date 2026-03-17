#include <algorithm>
#include <cstdlib>
#include "pdqsort.h" // Nhúng trực tiếp thuật toán pdqsort

extern "C"
{

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

    void swap_elem(int &a, int &b)
    {
        int temp = a;
        a = b;
        b = temp;
    }

    int partition(int *arr, int low, int high, int pivot_idx)
    {
        swap_elem(arr[pivot_idx], arr[high]);
        int pivot = arr[high];
        int i = low - 1;
        for (int j = low; j < high; j++)
        {
            if (arr[j] <= pivot)
            {
                i++;
                swap_elem(arr[i], arr[j]);
            }
        }
        swap_elem(arr[i + 1], arr[high]);
        return i + 1;
    }

    // Các thuật toán kinh điển giữ nguyên
    EXPORT void qs_first(int *arr, int low, int high)
    {
        if (low < high)
        {
            int pi = partition(arr, low, high, low);
            qs_first(arr, low, pi - 1);
            qs_first(arr, pi + 1, high);
        }
    }

    EXPORT void qs_last(int *arr, int low, int high)
    {
        if (low < high)
        {
            int pi = partition(arr, low, high, high);
            qs_last(arr, low, pi - 1);
            qs_last(arr, pi + 1, high);
        }
    }

    EXPORT void qs_middle(int *arr, int low, int high)
    {
        if (low < high)
        {
            int pi = partition(arr, low, high, low + (high - low) / 2);
            qs_middle(arr, low, pi - 1);
            qs_middle(arr, pi + 1, high);
        }
    }

    EXPORT void qs_random(int *arr, int low, int high)
    {
        if (low < high)
        {
            int random_idx = low + rand() % (high - low + 1);
            int pi = partition(arr, low, high, random_idx);
            qs_random(arr, low, pi - 1);
            qs_random(arr, pi + 1, high);
        }
    }
    // 5. TRUNG VỊ CỦA 3 (Median of 3)
    int median_of_3(int *arr, int low, int high)
    {
        int mid = low + (high - low) / 2;
        if (arr[mid] < arr[low])
            swap_elem(arr[mid], arr[low]);
        if (arr[high] < arr[low])
            swap_elem(arr[high], arr[low]);
        if (arr[high] < arr[mid])
            swap_elem(arr[high], arr[mid]);
        return mid; // mid bây giờ là trung vị của 3 phần tử
    }

    EXPORT void qs_median_of_3(int *arr, int low, int high)
    {
        if (low < high)
        {
            int pivot_idx = median_of_3(arr, low, high);
            int pi = partition(arr, low, high, pivot_idx);
            qs_median_of_3(arr, low, pi - 1);
            qs_median_of_3(arr, pi + 1, high);
        }
    }

    // 6. TRUNG VỊ CỦA CÁC TRUNG VỊ (Median of Medians)
    // Insertion sort cho nhóm 5 phần tử
    void insertion_sort(int *arr, int low, int high)
    {
        for (int i = low + 1; i <= high; i++)
        {
            int key = arr[i];
            int j = i - 1;
            while (j >= low && arr[j] > key)
            {
                arr[j + 1] = arr[j];
                j--;
            }
            arr[j + 1] = key;
        }
    }

    int get_median_of_medians(int *arr, int low, int high)
    {
        int n = high - low + 1;
        if (n <= 5)
        {
            insertion_sort(arr, low, high);
            return low + n / 2;
        }
        int num_groups = (n + 4) / 5;
        for (int i = 0; i < num_groups; i++)
        {
            int group_low = low + i * 5;
            int group_high = std::min(low + i * 5 + 4, high);
            insertion_sort(arr, group_low, group_high);
            int median_idx = group_low + (group_high - group_low) / 2;
            swap_elem(arr[low + i], arr[median_idx]); // Đưa các trung vị lên đầu mảng
        }
        return get_median_of_medians(arr, low, low + num_groups - 1);
    }

    EXPORT void qs_median_of_medians(int *arr, int low, int high)
    {
        if (low < high)
        {
            int pivot_idx = get_median_of_medians(arr, low, high);
            int pi = partition(arr, low, high, pivot_idx);
            qs_median_of_medians(arr, low, pi - 1);
            qs_median_of_medians(arr, pi + 1, high);
        }
    }

    // 7. DUAL-PIVOT QUICKSORT
    EXPORT void qs_dual_pivot(int *arr, int low, int high)
    {
        if (low < high)
        {
            if (arr[low] > arr[high])
            {
                swap_elem(arr[low], arr[high]);
            }
            int p1 = arr[low];
            int p2 = arr[high];

            int i = low + 1;
            int j = high - 1;
            int k = low + 1;

            // Chia mảng thành 3 phần
            while (k <= j)
            {
                if (arr[k] < p1)
                {
                    swap_elem(arr[k], arr[i]);
                    i++;
                }
                else if (arr[k] >= p2)
                {
                    while (arr[j] > p2 && k < j)
                        j--;
                    swap_elem(arr[k], arr[j]);
                    j--;
                    if (arr[k] < p1)
                    {
                        swap_elem(arr[k], arr[i]);
                        i++;
                    }
                }
                k++;
            }
            i--;
            j++;
            swap_elem(arr[low], arr[i]);
            swap_elem(arr[high], arr[j]);

            // Đệ quy 3 nửa
            qs_dual_pivot(arr, low, i - 1);
            qs_dual_pivot(arr, i + 1, j - 1);
            qs_dual_pivot(arr, j + 1, high);
        }
    }
    // --- HÀM MỚI: Gọi trực tiếp pdqsort ---
    EXPORT void qs_pdqsort(int *arr, int low, int high)
    {
        // Hàm pdqsort nhận con trỏ đầu và con trỏ ngay sau phần tử cuối cùng
        pdqsort(arr + low, arr + high + 1);
    }
}
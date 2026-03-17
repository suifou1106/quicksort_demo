# Demo quicksort
1. run pip install -r requirements.txt.
2. Make sure you have g++ on your desktop (install here: https://www.msys2.org/).
3. run g++ -shared -o sort_engine.dll sort_engine.cpp -O3 every time you change sort_engine.cpp file.
4. run python ./gui_app.py
## (recommend run all above on virtual machine like venv or conda)
# Quicksort Evolution: A Comprehensive Pivot Strategy Benchmark

## Introduction

Quicksort is one of the most efficient and widely used sorting algorithms in computer science, operating on the **Divide and Conquer** principle. Its core mechanism involves selecting a "pivot" element, partitioning the array so that smaller elements are placed on the left and larger elements on the right, and then recursively applying the same process to the resulting sub-arrays.

However, Quicksort's real-world performance is heavily dependent on **how the pivot is chosen**. A good pivot divides the array into two roughly equal halves, resulting in highly optimized execution. A poor pivot—especially when dealing with already sorted, reverse-sorted, or highly duplicated data—can degrade the algorithm's performance drastically, causing stack overflows and severe slowdowns.

This repository explores the evolution of Quicksort by implementing, analyzing, and benchmarking various pivot selection strategies. It traces the journey from the classic, naive implementations of the 1960s to modern, hardware-optimized hybrid algorithms like `pdqsort`.
# Pseudo code
## 1. Standard Quicksort Framework & Basic Pivots
     ALGORITHM QuickSort(A[l..r])
     //Sorts a subarray by quicksort
     //Input: Subarray of array A[0..n-1], defined by its left and right indices l and r
     //Output: Subarray A[l..r] sorted in nondecreasing order
     if l < r
         p_idx ← ChoosePivot(A, l, r)  // Choose pivot using one of the strategies below
         swap(A[l], A[p_idx])          // Move pivot to the first position
         s ← Partition(A, l, r)        // Partition the subarray
         QuickSort(A[l..s - 1])
         QuickSort(A[s + 1..r])
     
     ALGORITHM Partition(A[l..r])
     //Partitions a subarray by Hoare's algorithm
     //Input: Subarray of array A[0..n-1], defined by its left and right indices l and r (l < r)
     //Output: Partition of A[l..r], with the split position returned as this function's value
     p ← A[l]
     i ← l; j ← r + 1
     repeat
         repeat i ← i + 1 until A[i] ≥ p or i ≥ r
         repeat j ← j - 1 until A[j] ≤ p
         swap(A[i], A[j])
     until i ≥ j
     swap(A[i], A[j]) // Undo last swap
     swap(A[l], A[j])
     return j
### Pivot Selection Strategies (Choose_Pivot implementations):
     ALGORITHM ChoosePivotFirst(A[l..r])
     //Input: Subarray A[l..r]
     //Output: The index of the first element
     return l
     
     ALGORITHM ChoosePivotLast(A[l..r])
     //Input: Subarray A[l..r]
     //Output: The index of the last element
     return r
     
     ALGORITHM ChoosePivotMiddle(A[l..r])
     //Input: Subarray A[l..r]
     //Output: The index of the middle element
     return l + floor((r - l) / 2)
     
     ALGORITHM ChoosePivotRandom(A[l..r])
     //Input: Subarray A[l..r]
     //Output: A random index between l and r
     return RandomInteger(l, r)
     
     ALGORITHM ChoosePivotMedianOf3(A[l..r])
     //Input: Subarray A[l..r]
     //Output: The index of the median value among the first, middle, and last elements
     mid ← l + floor((r - l) / 2)
     return MedianOf3(A, l, mid, r) // Assuming MedianOf3 function is already defined
## 2. Median of Medians
     ALGORITHM ChoosePivotMedianOfMedians(A[l..r])
     //Input: Subarray A[l..r]
     //Output: The index of the median of medians
     n ← r - l + 1
     if n ≤ 5
         InsertionSort(A[l..r])
         return l + floor(n / 2)
     
     // Divide the array into groups of 5 elements
     numGroups ← ceil(n / 5)
     for i ← 0 to numGroups - 1
         groupLeft ← l + i * 5
         groupRight ← min(l + i * 5 + 4, r)
         InsertionSort(A[groupLeft..groupRight])
         medianIdx ← groupLeft + floor((groupRight - groupLeft) / 2)
         swap(A[l + i], A[medianIdx]) // Move medians to the front of the subarray
     
     // Recursively find the median of the medians
     return ChoosePivotMedianOfMedians(A[l..l + numGroups - 1])
## 3. Dual-Pivot Quicksort
     ALGORITHM DualPivotQuickSort(A[l..r])
     //Sorts a subarray using dual-pivot quicksort strategy
     //Input: Subarray A[l..r]
     //Output: Subarray A[l..r] sorted in nondecreasing order
     if l < r
         if A[l] > A[r]
             swap(A[l], A[r])
         p ← A[l]
         q ← A[r]
         
         j ← l + 1; g ← r - 1; k ← l + 1
         while k ≤ g
             if A[k] < p
                 swap(A[k], A[j])
                 j ← j + 1
             else if A[k] ≥ q
                 while A[g] > q and k < g
                     g ← g - 1
                 swap(A[k], A[g])
                 g ← g - 1
                 if A[k] < p
                     swap(A[k], A[j])
                     j ← j + 1
             k ← k + 1
             
         j ← j - 1
         g ← g + 1
         swap(A[l], A[j])
         swap(A[r], A[g])
         
         DualPivotQuickSort(A[l..j - 1])
         DualPivotQuickSort(A[j + 1..g - 1])
         DualPivotQuickSort(A[g + 1..r])
## 4. pdqsort (Pattern-defeating Quicksort)
     ALGORITHM PdqSort(A[l..r], badAllowed)
     //Sorts a subarray using Pattern-Defeating Quicksort strategy
     //Input: Subarray A[l..r], and the allowed number of bad partitions
     //Output: Subarray A[l..r] sorted in nondecreasing order
     //Initial call: PdqSort(A, 0, n-1, floor(log2(n)))
     
     n ← r - l + 1
     if n < 24
         InsertionSort(A[l..r])
         return
     
     if badAllowed = 0
         HeapSort(A[l..r])
         return
     
     p_idx ← PdqChoosePivot(A[l..r]) // Uses Tukey's Ninther strategy for large arrays
     swap(A[l], A[p_idx])
     
     s ← Partition(A, l, r)
     
     // Check for "bad partition" (highly unbalanced split)
     leftSize ← s - l
     rightSize ← r - s
     if leftSize < n / 8 or rightSize < n / 8
         badAllowed ← badAllowed - 1
         // In practice, pdqsort scrambles some elements here to break patterns
         
     PdqSort(A[l..s - 1], badAllowed)
     PdqSort(A[s + 1..r], badAllowed)
     
## Complexity Summary

The table below summarizes the theoretical time and space complexities for each pivot selection strategy. Note that while some algorithms share the same asymptotic notation, their constant factors (real-world execution times) vary significantly.

| Pivot Strategy | Best Time | Average Time | Worst Time | Space (Worst) | Key Characteristic |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **First / Last / Middle** | $O(N \log N)$ | $O(N \log N)$ | $O(N^2)$ | $O(N)$ | Simple to implement but highly vulnerable to sorted or patterned arrays. |
| **Random** | $O(N \log N)$ | $O(N \log N)$ | $O(N^2)$ | $O(N)$ | Avoids the worst-case on structured data, but random number generation adds overhead. |
| **Median of 3** | $O(N \log N)$ | $O(N \log N)$ | $O(N^2)$ | $O(\log N)$ | Excellent heuristic for real-world data; avoids $O(N^2)$ on sorted arrays. |
| **Median of Medians** | $O(N \log N)$ | $O(N \log N)$ | $O(N \log N)$ | $O(\log N)$ | Mathematically guarantees $O(N \log N)$ in all cases, but practically slow due to heavy constant factors. |
| **Dual-Pivot** | $O(N \log N)$ | $O(N \log N)$ | $O(N^2)$ | $O(\log N)$ | Uses 2 pivots to divide data into 3 partitions. Highly cache-efficient; default in Java. |
| **pdqsort (Hybrid)** | $O(N)$* | $O(N \log N)$ | $O(N \log N)$ | $O(\log N)$ | Falls back to Heapsort to strictly prevent $O(N^2)$ and uses Insertion Sort for small arrays. |

*\* `pdqsort` achieves linear time $O(N)$ if its pattern-defeating heuristics detect that the input array is already sorted.*

---

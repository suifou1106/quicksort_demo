# Demo quicksort
1. run pip install -r requirements.txt.
2. Make sure you have g++ on your desktop (install here: https://www.msys2.org/).
3. run g++ -shared -o sort_engine.dll sort_engine.cpp -O3 every time you change sort_engine.cpp file.
4. run python ./gui_app.py
## (recommend run all above on virtual machine like venv or conda)
# Pseudo code
## 1. Standard Quicksort Framework & Basic Pivots
// --- MAIN QUICKSORT FRAMEWORK ---
Function Quicksort_Classic(A, low, high):
    If low < high:
        // 1. Choose pivot index using one of the strategies below
        pivot_idx = Choose_Pivot(A, low, high) 
        
        // 2. Swap pivot to the end of the array for easy partitioning
        Swap(A[pivot_idx], A[high])
        
        // 3. Partition and get the exact position of the pivot
        pi = Partition(A, low, high)
        
        // 4. Recursively sort the two halves
        Quicksort_Classic(A, low, pi - 1)
        Quicksort_Classic(A, pi + 1, high)

// --- LOMUTO PARTITION SCHEME ---
Function Partition(A, low, high):
    pivot_value = A[high]
    i = low - 1
    
    For j from low to high - 1:
        If A[j] <= pivot_value:
            i = i + 1
            Swap(A[i], A[j])
            
    Swap(A[i + 1], A[high])
    Return i + 1
### Pivot Selection Strategies (Choose_Pivot implementations):
// 1. First Pivot
Function Choose_Pivot_First(A, low, high):
    Return low

// 2. Last Pivot
Function Choose_Pivot_Last(A, low, high):
    Return high

// 3. Middle Pivot
Function Choose_Pivot_Middle(A, low, high):
    Return low + (high - low) / 2

// 4. Random Pivot
Function Choose_Pivot_Random(A, low, high):
    Return Random_Integer(from low to high)

// 5. Median of 3
Function Choose_Pivot_MedianOf3(A, low, high):
    mid = low + (high - low) / 2
    // Sort A[low], A[mid], A[high] to find the median value
    If A[low] > A[mid]: Swap(A[low], A[mid])
    If A[low] > A[high]: Swap(A[low], A[high])
    If A[mid] > A[high]: Swap(A[mid], A[high])
    
    // A[mid] is now the median
    Return mid
## 2. Median of Medians
Function Choose_Pivot_MoM(A, low, high):
    num_elements = high - low + 1
    
    // If the array has 5 or fewer elements, use insertion sort and return the median
    If num_elements <= 5:
        InsertionSort(A, low, high)
        Return low + num_elements / 2
        
    // Divide the array into blocks of 5 elements
    num_blocks = Ceiling(num_elements / 5)
    Create median_array of size num_blocks
    
    For i from 0 to num_blocks - 1:
        start = low + i * 5
        end = Min(start + 4, high)
        InsertionSort(A, start, end)
        median_array[i] = A[start + (end - start) / 2]
        
    // Recursively find the median of the median_array
    pivot_value = Choose_Pivot_MoM(median_array, 0, num_blocks - 1)
    
    // Find and return the index of pivot_value in the original array A
    Return Index_Of(pivot_value in array A from low to high)
## 3. Dual-Pivot Quicksort
Function DualPivotQuicksort(A, low, high):
    If low < high:
        // Ensure left pivot (P1) <= right pivot (P2)
        If A[low] > A[high]:
            Swap(A[low], A[high])
            
        p1 = A[low]
        p2 = A[high]
        
        i = low + 1   // Boundary for elements < P1
        k = low + 1   // Current element index
        j = high - 1  // Boundary for elements > P2
        
        While k <= j:
            If A[k] < p1:
                Swap(A[k], A[i])
                i = i + 1
            Else if A[k] >= p2:
                While A[j] > p2 and k < j:
                    j = j - 1
                Swap(A[k], A[j])
                j = j - 1
                // Check the swapped element again
                If A[k] < p1:
                    Swap(A[k], A[i])
                    i = i + 1
            k = k + 1
            
        // Move the two pivots to their correct final positions
        i = i - 1
        j = j + 1
        Swap(A[low], A[i])
        Swap(A[high], A[j])
        
        // Recursively sort the 3 partitions (< P1, between P1 & P2, > P2)
        DualPivotQuicksort(A, low, i - 1)
        DualPivotQuicksort(A, i + 1, j - 1)
        DualPivotQuicksort(A, j + 1, high)
## 4. pdqsort (Pattern-defeating Quicksort)
Function pdqsort_core(A, low, high, bad_partition_limit):
    size = high - low + 1
    
    // 1. Fallback 1: Array is too small -> Use Insertion Sort
    If size < 24:
        InsertionSort(A, low, high)
        Return
        
    // 2. Fallback 2: Prevent O(N^2) -> Switch to Heapsort if too many bad partitions
    If bad_partition_limit == 0:
        Heapsort(A, low, high)
        Return
        
    // 3. Smart Pivot Selection
    If size > 128:
        pivot_idx = Ninther(A, low, high) // Median of 3 medians
    Else:
        pivot_idx = Median_of_3(A, low, high) // Median of 3
        
    // 4. Partitioning (using branchless partition for hardware optimization)
    Swap(A[low], A[pivot_idx])
    split_idx = Branchless_Partition(A, low, high)
    
    // 5. Check for bad partition (Pattern-defeating capability)
    len_left = split_idx - low
    len_right = high - split_idx
    If len_left < (size / 8) Or len_right < (size / 8):
        bad_partition_limit = bad_partition_limit - 1
        
    // 6. Handle duplicates (if the element next to the pivot equals the pivot)
    If A[split_idx + 1] == A[split_idx]:
        split_idx = Partition_Equal_Elements(A, split_idx + 1, high, A[split_idx])
        
    // 7. Smart Recursion: Always recurse on the smaller partition first to save Stack space
    If len_left < len_right:
        pdqsort_core(A, low, split_idx - 1, bad_partition_limit)
        pdqsort_core(A, split_idx + 1, high, bad_partition_limit)
    Else:
        pdqsort_core(A, split_idx + 1, high, bad_partition_limit)
        pdqsort_core(A, low, split_idx - 1, bad_partition_limit)

// Main wrapper function called by the user
Function pdqsort(A):
    bad_partition_limit = Log2(Length(A))
    pdqsort_core(A, 0, Length(A) - 1, bad_partition_limit)

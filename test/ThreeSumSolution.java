import java.util.*;

public class ThreeSumSolution {

    public List<List<Integer>> threeSum(int[] nums) {
        List<List<Integer>> result = new ArrayList<>();
        
        // Sort the array to facilitate the two-pointer approach
        Arrays.sort(nums);
        
        // Traverse through each number, considering it as the first element of the triplet
        for (int i = 0; i < nums.length - 2; i++) {
            // Skip duplicate values for the first element
            if (i > 0 && nums[i] == nums[i - 1]) {
                continue;
            }
            
            int target = -nums[i]; // target for the two-pointer search
            int left = i + 1;
            int right = nums.length - 1;

            // Two-pointer search for the remaining two elements
            while (left < right) {
                int sum = nums[left] + nums[right];
                
                if (sum == target) {
                    // Add the triplet to the result
                    result.add(Arrays.asList(nums[i], nums[left], nums[right]));
                    
                    // Move pointers and skip duplicates
                    left++;
                    right--;
                    
                    // Skip duplicates for the second element
                    while (left < right && nums[left] == nums[left - 1]) {
                        left++;
                    }
                    
                    // Skip duplicates for the third element
                    while (left < right && nums[right] == nums[right + 1]) {
                        right--;
                    }
                } else if (sum < target) {
                    left++; // Increase sum by moving the left pointer
                } else {
                    right--; // Decrease sum by moving the right pointer
                }
            }
        }
        
        return result;
    }

    // Testing the solution
    public static void main(String[] args) {
        ThreeSumSolution solution = new ThreeSumSolution();
        int[] nums = {-1, 0, 1, 2, -1, -4};
        
        List<List<Integer>> result = solution.threeSum(nums);
        System.out.println("Triplets with sum zero:");
        for (List<Integer> triplet : result) {
            System.out.println(triplet);
        }
    }
}

import java.util.*;

public class TripletSum {

    public List<List<Integer>> findTriplets(int[] array) {
        List<List<Integer>> results = new ArrayList<>();

        // Exit early if the array is too small to have a triplet
        if (array == null || array.length < 3) {
            return results;
        }

        // Sort to use a two-pointer approach
        Arrays.sort(array);

        // Loop through the array, treating each element as the first in a potential triplet
        for (int first = 0; first < array.length - 2; first++) {
            // Skip duplicate starting elements
            if (first > 0 && array[first] == array[first - 1]) {
                continue;
            }

            int requiredSum = -array[first];
            int pointer1 = first + 1;
            int pointer2 = array.length - 1;

            // Two-pointer approach to find pairs that sum to the required value
            while (pointer1 < pointer2) {
                int currentSum = array[pointer1] + array[pointer2];
                
                if (currentSum == requiredSum) {
                    // Store the found triplet
                    results.add(Arrays.asList(array[first], array[pointer1], array[pointer2]));
                    
                    // Move both pointers inward and skip duplicates
                    pointer1++;
                    pointer2--;

                    // Skip duplicate second element values
                    while (pointer1 < pointer2 && array[pointer1] == array[pointer1 - 1]) {
                        pointer1++;
                    }
                    
                    // Skip duplicate third element values
                    while (pointer1 < pointer2 && array[pointer2] == array[pointer2 + 1]) {
                        pointer2--;
                    }
                } else if (currentSum < requiredSum) {
                    pointer1++;
                } else {
                    pointer2--;
                }
            }
        }

        return results;
    }

    // Testing the modified solution
    public static void main(String[] args) {
        TripletSum solution = new TripletSum();
        int[] sampleArray = {-1, 0, 1, 2, -1, -4};

        List<List<Integer>> results = solution.findTriplets(sampleArray);
        System.out.println("Triplets with sum zero:");
        for (List<Integer> triplet : results) {
            System.out.println(triplet);
        }
    }
}

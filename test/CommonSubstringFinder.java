public class CommonSubstringFinder {
   public static void main(String[] args) {
       String string1 = "abcdef";
       String string2 = "zbcdf";
       
       String longestSubstring = findLongestCommonSubstring(string1, string2);
       System.out.println("The longest common substring is: " + longestSubstring);
   }
   
   public static String findLongestCommonSubstring(String string1, String string2) {
       int longestLength = 0;
       int substringEndIndex = 0;
       int[][] lookupTable = new int[string1.length() + 1][string2.length() + 1];
       
       for (int i = 1; i <= string1.length(); i++) {
           for (int j = 1; j <= string2.length(); j++) {
               if (string1.charAt(i - 1) == string2.charAt(j - 1)) {
                   lookupTable[i][j] = lookupTable[i - 1][j - 1] + 1;
                   if (lookupTable[i][j] > longestLength) {
                       longestLength = lookupTable[i][j];
                       substringEndIndex = i;
                   }
               } else {
                   lookupTable[i][j] = 0;
               }
           }
       }
       
       return string1.substring(substringEndIndex - longestLength, substringEndIndex);
   }
}

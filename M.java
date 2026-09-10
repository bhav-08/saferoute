import java.util.*;

class ProductExceptSelf {

    static int[] productExceptSelf(int[] nums) {

        int n = nums.length;
        int[] answer = new int[n];

        // Forward pass: product of elements on the left
        int leftProduct = 1;

        for (int i = 0; i < n; i++) {
            answer[i] = leftProduct;
            leftProduct = leftProduct * nums[i];
        }

        // Backward pass: product of elements on the right
        int rightProduct = 1;

        for (int i = n - 1; i >= 0; i--) {
            answer[i] = answer[i] * rightProduct;
            rightProduct = rightProduct * nums[i];
        }

        return answer;
    }

    public static void main(String[] args) {

        int[] nums = {1, 2, 3, 4};

        int[] result = productExceptSelf(nums);

        System.out.print("Output: ");

        for (int i = 0; i < result.length; i++) {
            System.out.print(result[i] + " ");
        }
    }
}
import java.util.*;

class ThreeSum
{
    static int[][] threeSum(int[] nums)
    {
        Arrays.sort(nums);

        ArrayList<int[]> list=new ArrayList<>();

        for(int i=0;i<nums.length-2;i++)
        {
            if(i>0 && nums[i]==nums[i-1])
                continue;

            int left=i+1;
            int right=nums.length-1;

            while(left<right)
            {
                int sum=nums[i]+nums[left]+nums[right];

                if(sum==0)
                {
                    list.add(new int[]{nums[i],nums[left],nums[right]});

                    int leftValue=nums[left];
                    int rightValue=nums[right];

                    while(left<right && nums[left]==leftValue)
                        left++;

                    while(left<right && nums[right]==rightValue)
                        right--;
                }
                else if(sum<0)
                {
                    left++;
                }
                else
                {
                    right--;
                }
            }
        }

        int[][] result=new int[list.size()][3];

        for(int i=0;i<list.size();i++)
        {
            result[i]=list.get(i);
        }

        return result;
    }

    public static void main(String[] args)
    {
        int[] nums={-1,0,1,2,-1,-4};

        int[][] result=threeSum(nums);

        for(int[] triplet:result)
        {
            System.out.println(Arrays.toString(triplet));
        }
    }
}
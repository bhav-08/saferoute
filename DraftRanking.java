import java.util.*;

class CricketPlayer implements Comparable<CricketPlayer> {

    private String name;
    private int matchesPlayed;
    private double battingAverage;
    private boolean injured;

    public CricketPlayer(String name, int matchesPlayed,
                         double battingAverage, boolean injured) {
        this.name = name;
        this.matchesPlayed = matchesPlayed;
        this.battingAverage = battingAverage;
        this.injured = injured;
    }

    public static boolean isDraftable(int matchesPlayed) {
        return matchesPlayed >= 10;
    }

    public static boolean isDraftable(int matchesPlayed, boolean injured) {
        return matchesPlayed >= 5 && !injured;
    }

    public int compareTo(CricketPlayer other) {
        return Double.compare(other.battingAverage, this.battingAverage);
    }

    public static String draftAndRank(CricketPlayer[] players) {

        CricketPlayer[] temp = new CricketPlayer[players.length];
        int count = 0;

        for (int i = 0; i < players.length; i++) {

            if (isDraftable(players[i].matchesPlayed) ||
                isDraftable(players[i].matchesPlayed, players[i].injured)) {

                temp[count] = players[i];
                count++;
            }
        }

        CricketPlayer[] draftable = Arrays.copyOf(temp, count);

        Arrays.sort(draftable);

        String result = "";

        for (int i = 0; i < draftable.length; i++) {
            result += (i + 1) + ". " + draftable[i].name;

            if (i < draftable.length - 1) {
                result += " | ";
            }
        }

        return result;
    }
}

public class DraftRanking {

    public static void main(String[] args) {

        CricketPlayer[] players = {
            new CricketPlayer("Virat", 15, 48.0, false),
            new CricketPlayer("Rahul", 7, 55.0, false),
            new CricketPlayer("Sameer", 3, 60.0, false),
            new CricketPlayer("Dev", 12, 20.0, true)
        };

        System.out.println(CricketPlayer.draftAndRank(players));
    }
}
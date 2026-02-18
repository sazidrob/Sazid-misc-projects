import java.util.Random;
import java.util.Scanner;

public class Main {
    private static final int SIDES = 6;
    private static final int DEFAULT_ROLL_COUNT = 1;

    public static void main(String[] args) {
        Random random = new Random();
        Scanner scanner = new Scanner(System.in);

        printTitle();
        int numberOfRolls = askForRollCount(scanner);
        runRollSession(random, numberOfRolls);

        System.out.println();
        System.out.println("Thanks for using the dice roller.");
        scanner.close();
    }

    private static void printTitle() {
        System.out.println("=================================");
        System.out.println("         Java Dice Roller        ");
        System.out.println("=================================");
    }

    private static int askForRollCount(Scanner scanner) {
        System.out.print("How many times should I roll the die? ");

        if (!scanner.hasNextInt()) {
            System.out.println("Input was not a number. Using default: " + DEFAULT_ROLL_COUNT);
            scanner.nextLine();
            return DEFAULT_ROLL_COUNT;
        }

        int value = scanner.nextInt();
        scanner.nextLine();

        if (value <= 0) {
            System.out.println("Number must be positive. Using default: " + DEFAULT_ROLL_COUNT);
            return DEFAULT_ROLL_COUNT;
        }

        return value;
    }

    private static void runRollSession(Random random, int numberOfRolls) {
        int sum = 0;

        for (int i = 1; i <= numberOfRolls; i++) {
            int currentRoll = rollDie(random);
            sum += currentRoll;
            System.out.println("Roll " + i + ": " + currentRoll + " " + toFaceLabel(currentRoll));
        }

        printSummary(numberOfRolls, sum);
    }

    private static int rollDie(Random random) {
        return random.nextInt(SIDES) + 1;
    }

    private static String toFaceLabel(int value) {
        switch (value) {
            case 1:
                return "[ONE]";
            case 2:
                return "[TWO]";
            case 3:
                return "[THREE]";
            case 4:
                return "[FOUR]";
            case 5:
                return "[FIVE]";
            case 6:
                return "[SIX]";
            default:
                return "[?]";
        }
    }

    private static void printSummary(int numberOfRolls, int sum) {
        double average = (double) sum / numberOfRolls;

        System.out.println("---------------------------------");
        System.out.println("Total rolls: " + numberOfRolls);
        System.out.println("Sum of rolls: " + sum);
        System.out.printf("Average roll: %.2f%n", average);
    }
}

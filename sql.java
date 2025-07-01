class Test {
    public void runQuery(String userInput) {
        String query = "SELECT * FROM users WHERE name = '" + userInput + "'";
        statement.executeQuery(query);  // Vulnerable to SQL injection
    }
}

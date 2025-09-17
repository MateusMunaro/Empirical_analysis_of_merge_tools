
public class DatabaseConnectionFactory {
    public static DatabaseConnection createConnection(String type, String url) {
        String driver;
        switch(type) {
            case "mysql":
                driver = "com.mysql.cj.jdbc.Driver";
                return DatabaseConnection.createInstance("mysql://" + url, driver);
            case "postgres":
                driver = "org.postgresql.Driver";
                return DatabaseConnection.createInstance("postgresql://" + url, driver);
            case "oracle":
                driver = "oracle.jdbc.driver.OracleDriver";
                return DatabaseConnection.createInstance("oracle:thin:@" + url, driver);
            default:
                throw new IllegalArgumentException("Unknown database type: " + type);
        }
    }
    
    public static DatabaseConnection createDefaultConnection(String url) {
        return DatabaseConnection.createInstance(url, "default-driver");
    }
    
    // Method to get singleton instance with specific database type
    public static DatabaseConnection getSingletonConnection(String type, String url) {
        DatabaseConnection.resetInstance();
        DatabaseConnection instance = DatabaseConnection.getInstance(url);
        return instance;
    }
}
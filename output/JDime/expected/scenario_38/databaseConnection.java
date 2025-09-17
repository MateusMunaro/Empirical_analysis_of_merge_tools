public class DatabaseConnection {
    private static DatabaseConnection instance;
    private String url;
    private String driver;
    private String connectionPool;
    
    // Private constructor for singleton pattern and factory access
    private DatabaseConnection(String url, String driver) {
        this.url = url;
        this.driver = driver;
        this.connectionPool = "default-pool";
    }
    
    // Singleton pattern method (from left)
    public static DatabaseConnection getInstance(String url) {
        if (instance == null) {
            instance = new DatabaseConnection(url, "default");
        }
        return instance;
    }
    
    // Factory-friendly constructor access (package-private for factory)
    static DatabaseConnection createInstance(String url, String driver) {
        return new DatabaseConnection(url, driver);
    }
    
    public void connect() {
        System.out.println("Connecting to: " + url + " using driver: " + driver);
    }
    
    public void setConnectionPool(String pool) {
        this.connectionPool = pool;
    }
    
    public static void resetInstance() {
        instance = null;
    }
}


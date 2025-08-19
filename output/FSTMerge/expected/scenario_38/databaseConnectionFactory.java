
public class DatabaseConnectionFactory {
    public static DatabaseConnection createConnection(String type, String url) {
        switch(type) {
            case "mysql":
                return new DatabaseConnection("mysql://" + url);
            case "postgres":
                return new DatabaseConnection("postgresql://" + url);
            default:
                throw new IllegalArgumentException("Unknown database type");
        }
    }
}
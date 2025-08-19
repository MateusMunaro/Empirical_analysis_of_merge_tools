
public class DatabaseConnection {
  private static DatabaseConnection instance;

  private String url;

  private DatabaseConnection(String url) {
    this.url = url;
  }

  public static DatabaseConnection getInstance(String url) {
    if (instance == null) {
      instance = new DatabaseConnection(url);
    }
    return instance;
  }
}

public class DatabaseConnectionFactory {
  public static DatabaseConnection createConnection(String type, String url) {
    switch (type) {
      case "mysql":
      return new DatabaseConnection("mysql://" + url);
      case "postgres":
      return new DatabaseConnection("postgresql://" + url);
      default:
      throw new IllegalArgumentException("Unknown database type");
    }
  }
}
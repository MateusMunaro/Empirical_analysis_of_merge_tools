public abstract class Entity {
    private Long id;
    protected Date createdAt;
}

public class Product extends Entity {
    private String name;
}
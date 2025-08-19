public interface Identifiable {
     Long getId();
     void setId(Long id);
}

public interface Timestamped {
     Date getCreatedAt();
}

public abstract class Entity {
    private Long id;
    protected Date createdAt;
}

<<<<<<< ours
public class Product extends Entity
=======
public class Product implements Identifiable, Timestamped
>>>>>>> theirs
 {
    private Long id;
    private String name;
    private Date createdAt;
    
    @Override
    public Long getId() { return id; }
    
    @Override
    public void setId(Long id) { this.id = id; }
    
    @Override
    public Date getCreatedAt() { return createdAt; }
}
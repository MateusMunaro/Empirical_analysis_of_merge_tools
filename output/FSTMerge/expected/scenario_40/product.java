public interface Identifiable {
    Long getId();
    void setId(Long id);
}

public interface Timestamped {
    Date getCreatedAt();
}

public class Product implements Identifiable, Timestamped {
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
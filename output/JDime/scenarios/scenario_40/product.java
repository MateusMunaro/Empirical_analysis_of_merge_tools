

<<<<<<< ./senarios_merge_base/JDime/scenario_40/left/product.java
public abstract class Entity {
  private Long id;

  protected Date createdAt;
}
=======
public interface Identifiable {
  Long getId();

  void setId(Long id);
}
>>>>>>> ./senarios_merge_base/JDime/scenario_40/right/product.java


public interface Timestamped {
  Date getCreatedAt();
}

public class Product extends Entity implements Identifiable, Timestamped {
  private String name;

  private Date createdAt;

  @Override public Long getId() {
    return id;
  }

  @Override public void setId(Long id) {
    this.id = id;
  }

  @Override public Date getCreatedAt() {
    return createdAt;
  }
}
public class PersonEntity {
    private int id;
    private String name;
}
public class PersonRepository {
    public void save(PersonEntity entity) { }
}
public class PersonValidator {
    public void validate(PersonEntity entity) { }
}
public interface Persistable {
     void save();
}
public interface Validatable {
     void validate();
}
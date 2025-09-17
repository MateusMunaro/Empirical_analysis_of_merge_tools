public interface Persistable {
    void save();
}
public interface Validatable {
    void validate();
}
public class Person implements Persistable, Validatable {
    private int id;
    private String name;
    public void save() { }
    public void validate() { }
}
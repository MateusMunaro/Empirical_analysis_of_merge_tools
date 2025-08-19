

<<<<<<< ./senarios_merge_base/JDime/scenario_35/left/person.java
public interface Persistable {
  void save();
}
=======
public class PersonEntity {
  private int id;

  private String name;
}
>>>>>>> ./senarios_merge_base/JDime/scenario_35/right/person.java



<<<<<<< ./senarios_merge_base/JDime/scenario_35/left/person.java
public interface Validatable {
  void validate();
}
=======
public class PersonRepository {
  public void save(PersonEntity entity) {
  }
}
>>>>>>> ./senarios_merge_base/JDime/scenario_35/right/person.java



<<<<<<< ./senarios_merge_base/JDime/scenario_35/left/person.java
public class Person implements Persistable, Validatable {
  private int id;

  private String name;

  public void save() {
  }

  public void validate() {
  }
}
=======
public class PersonValidator {
  public void validate(PersonEntity entity) {
  }
}
>>>>>>> ./senarios_merge_base/JDime/scenario_35/right/person.java


public class Person {
  private int id;

  private String name;

  private String email;


<<<<<<< ./senarios_merge_base/JDime/scenario_4/left/Person.java
  private Float phone;
=======
  private int phone;
>>>>>>> ./senarios_merge_base/JDime/scenario_4/right/Person.java


  public Person() {
  }

  public Person(int id, String name, String email, 
<<<<<<< ./senarios_merge_base/JDime/scenario_4/left/Person.java
  Float phone
=======
  int phone
>>>>>>> ./senarios_merge_base/JDime/scenario_4/right/Person.java
  ) {
    this.id = id;
    this.name = name;
    this.email = email;
    this.phone = phone;
  }

  public int getId() {
    return id;
  }

  public void setId(int id) {
    this.id = id;
  }

  public String getName() {
    return name;
  }

  public void setName(String name) {
    this.name = name;
  }

  public String getEmail() {
    return email;
  }

  public void setEmail(String email) {
    this.email = email;
  }


<<<<<<< ./senarios_merge_base/JDime/scenario_4/left/Person.java
  public Float getPhone() {
    return phone;
  }
=======
  public int getPhone() {
    return phone;
  }
>>>>>>> ./senarios_merge_base/JDime/scenario_4/right/Person.java


  public void setPhone(String phone) {
    this.phone = phone;
  }

  @Override public String toString() {
    return "Person{id=" + id + ", name=\'" + name + "\'}";
  }
}
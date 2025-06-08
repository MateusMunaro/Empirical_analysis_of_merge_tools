import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class PersonService {
    private Map<Integer, Person> personDB;
    
    public PersonService() {
        this.personDB = new HashMap<>();
    }
    
    public Person save(Person person) {
        personDB.put(person.getId(), person);
        return person;
    }
    
    public Person findById(int id) {
        return personDB.get(id);
    }
    
    public List<Person> findAll() {
        return new ArrayList<>(personDB.values());
    }
    
    public void delete(int id) {
        personDB.remove(id);
    }
    
    public boolean exists(int id) {
        return personDB.containsKey(id);
    }
    
    public Person update(Person person) {
        if (exists(person.getId())) {
            return save(person);
        }
        return null;
    }
}
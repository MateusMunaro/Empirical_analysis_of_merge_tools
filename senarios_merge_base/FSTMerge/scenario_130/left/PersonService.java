import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class PersonService {
    private Map<Integer, NewPerson> personDB;
    
    public PersonService() {
        this.personDB = new HashMap<>();
    }
    
    public Person save(NewPerson person) {
        personDB.put(person.getId(), person);
        return person;
    }
    
    public NewPerson findById(int id) {
        return personDB.get(id);
    }
    
    public List<NewPerson> findAll() {
        return new ArrayList<>(personDB.values());
    }
    
    public void delete(int id) {
        personDB.remove(id);
    }
    
    public boolean exists(int id) {
        return personDB.containsKey(id);
    }
    
    public NewPerson update(NewPerson person) {
        if (exists(person.getId())) {
            return save(person);
        }
        return null;
    }
}
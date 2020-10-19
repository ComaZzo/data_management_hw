SELECT 'ФИО: Чуваев Павел Сергеевич'

CREATE TABLE IF NOT EXISTS films(
  id INT PRIMARY KEY AUTO_INCREMENT,
  country TEXT NOT NULL,
  box_office INT,
  release_date DATE);
  
CREATE TABLE IF NOT EXISTS persons(
  id INT PRIMARY KEY AUTO_INCREMENT,
  fio TEXT NOT NULL);
  
 CREATE TABLE IF NOT EXISTS persons2context(
  person_id INT NOT NULL,
  film_id INT NOT NULL,
  person_type TEXT NOT NULL,
  FOREIGN KEY (person_id) REFERENCES persons(id),
  FOREIGN KEY (film_id) REFERENCES films(id));

INSERT INTO 
  films (country, box_office, release_date)
VALUES 
  ('New Zealand, USA', 1118887224, '2003-12-01');
  
 INSERT INTO 
  films (country, box_office, release_date)
 VALUES 
  ('USA', 286801374, '1999-12-06');
  
INSERT INTO 
  films (country, box_office, release_date)
VALUES 
  ('USA', 23875127, '1998-12-30');
  
INSERT INTO 
  films (country, box_office, release_date)
VALUES 
  ('USA', 213928762, '1994-05-21');
  
INSERT INTO 
  films (country, box_office, release_date)
VALUES 
  ('USA, UK', 1003045358, '2008-07-14');
  
INSERT INTO 
  persons(fio)
values
  ('Peter Jackson');
  
INSERT INTO 
  persons(fio)
values
  ('Tom Hanks');
  
INSERT INTO 
  persons(fio)
values
  ('Edward Norton');
  
INSERT INTO 
  persons(fio)
values
  ('Quentin Tarantino');

INSERT INTO 
  persons(fio)
values
  ('Heath Ledger');
  
INSERT INTO 
  persons2context (person_id, film_id, person_type)
VALUES
  (1,1,'producer');  
  
INSERT INTO 
  persons2context (person_id, film_id, person_type)
VALUES
  (2,2,'actor');  
  
INSERT INTO 
  persons2context (person_id, film_id, person_type)
VALUES
  (3,3,'actor');  
  
INSERT INTO 
  persons2context (person_id, film_id, person_type)
VALUES
  (4,4,'producer, screenwriter');  
  
INSERT INTO 
  persons2context (person_id, film_id, person_type)
VALUES
  (5,5,'actor');
  
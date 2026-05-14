CREATE TABLE IF NOT EXISTS students (
    id        SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS grades (
    id           SERIAL PRIMARY KEY,
    student_id   INTEGER  NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    group_number VARCHAR(50) NOT NULL,
    grade_date   DATE NOT NULL,
    grade        SMALLINT NOT NULL CHECK (grade BETWEEN 1 AND 5),
    uploaded_at  TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_grades_student_id ON grades(student_id);
CREATE INDEX IF NOT EXISTS idx_grades_grade      ON grades(grade);

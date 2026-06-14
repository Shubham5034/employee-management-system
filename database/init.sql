CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    department VARCHAR(100),
    salary INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


INSERT INTO employees(name, department, salary)
VALUES
('John','Engineering',80000),
('Alice','IT',90000);

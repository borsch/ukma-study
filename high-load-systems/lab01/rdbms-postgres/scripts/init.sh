#!/bin/bash

set -e
set -u

echo "  Creating database '$POSTGRES_DB'"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
  drop database if exists $POSTGRES_DB;
  create database $POSTGRES_DB;
  grant all privileges on database $POSTGRES_DB to $POSTGRES_USER;
EOSQL


# set default schema
export PGDATABASE=$POSTGRES_DB

echo 'create tables'
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
create table employee(
  id serial primary key,
  login varchar(70) not null unique
);

create table company(
  id serial primary key,
  name varchar(70) not null unique,
  city varchar(50) not null
);

create table work_at(
  company_id serial not null references company(id),
  employee_id serial not null references employee(id),
  start_work date not null,
  end_work date default null
);

create table skills(
  id serial primary key,
  name varchar(50) not null unique
);

create table employee_skill(
  employee_id serial not null references employee(id),
  skill_id serial not null references skills(id)
);
EOSQL

echo 'insert data'
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
insert into company (name, city) values
('company1', 'city1'),
('company2', 'city1'),
('company3', 'city1'),
('company4', 'city2'),
('company5', 'city3'),
('company6', 'city3'),
('company7', 'city4'),
('company8', 'city5'),
('company9', 'city6');


insert into employee(login) values
('login1-java'),
('login2-java'),
('login3-java'),
('login4-java'),
('login5-js'),
('login6-js'),
('login7-js'),
('login8-python'),
('login9-python'),
('login10-c++'),
('login11-rust'),
('login12-go');

insert into skills(name) values
('java'),
('spring'),
('hibernate'),
('angular'),
('react'),
('vue'),
('node'),
('python'),
('flask'),
('django'),
('c++'),
('stl'),
('unreal engine'),
('rust'),
('serde(rust)'),
('tokio(rust)'),
('go'),
('gin(go)'),
('beego(go)'),
('html'),
('css');

insert into work_at(employee_id, company_id, start_work, end_work) values
(1, 1, '2014-01-22', '2017-11-03'),
(1, 3, '2018-02-01', '2021-05-03'),
(1, 1, '2021-06-01', NULL),

(2, 1, '2015-04-22', '2016-03-10'),
(2, 2, '2016-04-01', NULL),

(3, 4, '2014-01-22', '2017-11-03'),
(3, 5, '2018-02-01', '2021-05-03'),
(3, 6, '2021-06-01', NULL),

(4, 3, '2014-01-22', '2017-11-03'),
(4, 6, '2018-02-01', '2021-05-03'),
(4, 8, '2021-06-01', NULL),

(5, 7, '2014-01-22', '2018-11-03'),
(5, 9, '2018-04-01', NULL),

(6, 6, '2014-01-22', '2018-11-03'),
(6, 7, '2018-12-01', '2020-03-03'),
(6, 9, '2020-05-01', '2022-11-03'),
(6, 3, '2023-01-10', NULL),

(7, 6, '2014-01-22', '2018-11-03'),
(7, 7, '2018-12-01', '2020-03-03'),
(7, 9, '2020-05-01', '2022-11-03'),
(7, 3, '2023-01-10', NULL),

(8, 6, '2014-01-22', '2018-11-03'),
(8, 7, '2018-12-01', '2020-03-03'),
(8, 9, '2020-05-01', '2022-11-03'),
(8, 3, '2023-01-10', NULL),

(9, 6, '2014-01-22', NULL),

(10, 1, '2014-01-22', '2018-11-03'),
(10, 4, '2018-12-01', '2020-03-03'),
(10, 8, '2020-05-01', '2022-11-03'),
(10, 2, '2023-01-10', NULL),

(11, 1, '2014-01-22', '2017-11-03'),
(11, 3, '2018-02-01', '2021-05-03'),
(11, 8, '2021-06-01', NULL),

(12, 1, '2014-01-22', '2017-11-03'),
(12, 3, '2018-02-01', '2021-05-03'),
(12, 8, '2021-06-01', '2022-12-30');

insert into employee_skill(employee_id, skill_id) values
(1, 1),
(1, 2),
(1, 3),
(1, 4),
(1, 20),
(1, 21),
(2, 1),
(2, 2),
(3, 1),
(3, 2),
(3, 3),
(4, 1),
(4, 2),
(4, 4),
(4, 20),
(4, 21),

(5, 4),
(5, 5),
(5, 20),
(5, 21),
(6, 6),
(6, 7),
(6, 20),
(7, 4),
(7, 20),
(7, 21),

(8, 8),
(8, 9),
(8, 10),
(9, 8),
(9, 10),
(9, 20),
(9, 21),

(10, 11),
(10, 12),
(10, 13),
(10, 20),
(10, 21),

(11, 14),
(11, 15),
(11, 16),

(12, 17),
(12, 18),
(12, 19),
(12, 4);

EOSQL

echo "----- SELECT RESULTS -------"
echo "CV by login"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
select e.login, s.name, c.name, wa.start_work, wa.end_work
from employee e
         join employee_skill es on e.id = es.employee_id
         join skills s on s.id = es.skill_id
         join work_at wa on e.id = wa.employee_id
         join company c on wa.company_id = c.id
where e.login = 'login1-java'
order by wa.start_work;
EOSQL

echo ''
echo "All skills in CV"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
select s.name
from skills s
         join employee_skill es on s.id = es.skill_id
         join employee e on es.employee_id = e.id
where e.login = 'login5-js';
EOSQL

echo ''
echo "All cities in single CV"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
select c.name, c.city, wa.start_work, wa.end_work
from employee e
         join work_at wa on e.id = wa.employee_id
         join company c on wa.company_id = c.id
where e.login = 'login8-python'
order by wa.start_work;
EOSQL

echo ''
echo "Skills of all employees that work in specific city(only current workplace)"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
select e.login, s.name
from employee e
         join employee_skill es on e.id = es.employee_id
         join skills s on s.id = es.skill_id
         join work_at wa on e.id = wa.employee_id and wa.end_work is null --current workplace only
         join company c on wa.company_id = c.id
where c.city = 'city1';
EOSQL

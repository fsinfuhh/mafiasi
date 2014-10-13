--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'SQL_ASCII';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

--
-- Data for Name: teaching_faculty; Type: TABLE DATA; Schema: public; Owner: mafiasi
--

INSERT INTO teaching_faculty (id, name, short_name) VALUES (1, 'Fakultät für Mathematik, Informatik und Naturwissenschaften', 'MIN');
INSERT INTO teaching_faculty (id, name, short_name) VALUES (2, 'Fakultät für Rechtswissenschaft', 'Rechtswissenschaft');
INSERT INTO teaching_faculty (id, name, short_name) VALUES (3, 'Fakultät Wirtschafts- und Sozialwissenschaften', 'WiSo');
INSERT INTO teaching_faculty (id, name, short_name) VALUES (4, 'Medizinische Fakultät', 'Medizin');
INSERT INTO teaching_faculty (id, name, short_name) VALUES (5, 'Fakultät für Erziehungwissenschaft', 'Erzwiss');
INSERT INTO teaching_faculty (id, name, short_name) VALUES (6, 'Fakultät für Geisteswissenschaften', 'Geisteswissenschaften');
INSERT INTO teaching_faculty (id, name, short_name) VALUES (7, 'Fakultät für Psychologie und Bewegungswissenschaft', 'PB');
INSERT INTO teaching_faculty (id, name, short_name) VALUES (8, 'Fakultät für Betriebswirtschaft', 'BWL');


--
-- Data for Name: teaching_department; Type: TABLE DATA; Schema: public; Owner: mafiasi
--

INSERT INTO teaching_department (id, name, faculty_id, short_name) VALUES (1, 'Fachbereich Informatik', 1, 'Informatik');
INSERT INTO teaching_department (id, name, faculty_id, short_name) VALUES (2, 'Fachbereich Physik', 1, 'Physik');
INSERT INTO teaching_department (id, name, faculty_id, short_name) VALUES (3, 'Fachbereich Mathematik', 1, 'Mathematik');
INSERT INTO teaching_department (id, name, faculty_id, short_name) VALUES (4, 'Zentrum für Bioinformatik', 1, 'ZBH');
INSERT INTO teaching_department (id, name, faculty_id, short_name) VALUES (5, 'Fachbereich Biologie', 1, 'Biologie');
INSERT INTO teaching_department (id, name, faculty_id, short_name) VALUES (6, 'Fachbereich Chemie', 1, 'Chemie');
INSERT INTO teaching_department (id, name, faculty_id, short_name) VALUES (7, 'Fachbereich Geowissenschaften', 1, 'Geowissenschaften');
INSERT INTO teaching_department (id, name, faculty_id, short_name) VALUES (8, 'Rechtswissenschaft', 2, 'Rechtswissenschaft');
INSERT INTO teaching_department (id, name, faculty_id, short_name) VALUES (9, 'Fachbereich Sozialwissenschaften', 3, 'Sozialwissenschaften');
INSERT INTO teaching_department (id, name, faculty_id, short_name) VALUES (10, 'Fachbereich Volkswirtschaftslehre', 3, 'VWL');
INSERT INTO teaching_department (id, name, faculty_id, short_name) VALUES (11, 'Fachbereich Sozialökonomie', 3, 'Sozialökonomie');
INSERT INTO teaching_department (id, name, faculty_id, short_name) VALUES (12, 'Medizin', 4, 'Medizin');
INSERT INTO teaching_department (id, name, faculty_id, short_name) VALUES (18, 'Fachbereich Evangelische Theologie', 6, 'Evangelische Theologie');
INSERT INTO teaching_department (id, name, faculty_id, short_name) VALUES (19, 'Fachbereich Sprache, Literatur und Medien', 6, 'SLM');
INSERT INTO teaching_department (id, name, faculty_id, short_name) VALUES (20, 'Fachbereich Geschichte', 6, 'Geschichte');
INSERT INTO teaching_department (id, name, faculty_id, short_name) VALUES (21, 'Fachbereich Philosophie', 6, 'Philosophie');
INSERT INTO teaching_department (id, name, faculty_id, short_name) VALUES (22, 'Fachbereich Kulturgeschichte und Kulturkunde', 6, 'Kulturgeschichte');
INSERT INTO teaching_department (id, name, faculty_id, short_name) VALUES (23, 'Fachbereich Asien-Afrika-Wissenschaften', 6, 'Asien-Afrika-Wissenschaften');
INSERT INTO teaching_department (id, name, faculty_id, short_name) VALUES (24, 'Institut für Katholische Theologie', 6, 'Katholische Theologie');
INSERT INTO teaching_department (id, name, faculty_id, short_name) VALUES (26, 'Betriebswirtschaft', 8, 'BWL');
INSERT INTO teaching_department (id, name, faculty_id, short_name) VALUES (25, 'Fachbereich Psychologie', 7, 'Psychologie');
INSERT INTO teaching_department (id, name, faculty_id, short_name) VALUES (27, 'Fachbereich Bewegungswissenschaft', 7, 'Bewegungswissenschaft');
INSERT INTO teaching_department (id, name, faculty_id, short_name) VALUES (13, 'Erziehungswissenschaft', 5, 'Erzwiss');


--
-- Name: teaching_department_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mafiasi
--

SELECT pg_catalog.setval('teaching_department_id_seq', 27, true);


--
-- Name: teaching_faculty_id_seq; Type: SEQUENCE SET; Schema: public; Owner: mafiasi
--

SELECT pg_catalog.setval('teaching_faculty_id_seq', 8, true);


--
-- PostgreSQL database dump complete
--


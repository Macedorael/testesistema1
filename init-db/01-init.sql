-- Script de inicialização do banco de dados MySQL
-- Este script será executado automaticamente quando o container MySQL for criado

-- Criar banco de dados se não existir
CREATE DATABASE IF NOT EXISTS consultorio_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Usar o banco de dados
USE consultorio_db;

-- Configurações de timezone
SET time_zone = '-03:00';

-- Configurações de charset
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- Mensagem de confirmação
SELECT 'Banco de dados consultorio_db inicializado com sucesso!' as status;
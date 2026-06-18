<?php
session_start();

if (isset($_SESSION["loggedin"]) && $_SESSION["loggedin"] === true) {
    header("Location: welcome.php");
    exit;
}

header("Location: login.php");
exit;
?>

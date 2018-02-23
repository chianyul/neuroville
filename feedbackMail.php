<?php
	// The message
	$name = $_POST['name'];
	$emailTo = "qianyu.liu@mail.mcgill.ca";
	$emailFrom = $_POST['email'];
	$subject = "Feedback Test from $emailFrom";
	$message = $_POST['message'];
	mail($to, $subject, $message);
?>
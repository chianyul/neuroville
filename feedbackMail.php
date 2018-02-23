<?php
	// The message
	$name = $_POST['name'];
	//$emailTo = "qianyu.liu@mail.mcgill.ca";
	$emailTo = "chainyu.liu@outlook.com";
	$emailFrom = $_POST['email'];
	$subject = "Feedback Test from $emailFrom";
	$message = $_POST['message'];
	mail($to, $subject, $message);
?>
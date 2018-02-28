<?php
	// The message
	$name = $_POST['name'];
	//$emailTo = "qianyu.liu@mail.mcgill.ca";
	$emailTo = "chianyu.liu@outlook.com";
	$emailFrom = $_POST['email'];
	//$emailFrom = "testFrom";
	$subject = "Feedback Test from $emailFrom";
	$message = $_POST['message'];
	//$message = "testMessage";
	@mail($to, $subject, $message);
?>
<?php
/**
 * The base configuration for WordPress
 *
 * The wp-config.php creation script uses this file during the installation.
 * You don't have to use the web site, you can copy this file to "wp-config.php"
 * and fill in the values.
 *
 * This file contains the following configurations:
 *
 * * Database settings
 * * Secret keys
 * * Database table prefix
 * * ABSPATH
 *
 * @link https://wordpress.org/documentation/article/editing-wp-config-php/
 *
 * @package WordPress
 */

// ** Database settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define( 'DB_NAME', 'megahubbusinessdb24' );

/** Database username */
define( 'DB_USER', 'Ultramegasuperadmin24' );

/** Database password */
define( 'DB_PASSWORD', 'MotdepassepasdutoutSecurise24!' );

/** Database hostname */
define( 'DB_HOST', 'localhost' );

/** Database charset to use in creating database tables. */
define( 'DB_CHARSET', 'utf8mb4' );

/** The database collate type. Don't change this if in doubt. */
define( 'DB_COLLATE', '' );

/**#@+
 * Authentication unique keys and salts.
 *
 * Change these to different unique phrases! You can generate these using
 * the {@link https://api.wordpress.org/secret-key/1.1/salt/ WordPress.org secret-key service}.
 *
 * You can change these at any point in time to invalidate all existing cookies.
 * This will force all users to have to log in again.
 *
 * @since 2.6.0
 */
define( 'AUTH_KEY',         'Jr Wt!swsPCw6rl cF17*!.&]jLEDnsVkUD!T%xT!rQGB,_+wXts!LVG.B:r+m= ' );
define( 'SECURE_AUTH_KEY',  'ishZ+[A[S!ahQf)+IgmWzjJL}W9x_-RD2KXpio%EIj+_KjrKxgZGGw6$,s%<*PTA' );
define( 'LOGGED_IN_KEY',    'sG.Oey=5{r^$v>[#^[t1uqbVgUp;Y=peM1v;,)1FjBYw9Y0Ix|XFl{Av%BL=sL-~' );
define( 'NONCE_KEY',        'q:?BsHFJ!W6^8[T$>043M?I&r,hT$Y~w5piRu)b$i2]sPx{ofT6;d#IK:tfSZ$#O' );
define( 'AUTH_SALT',        '`w6;<A,Ijlc[(,jM2o3SSYBD^,e+jB (wy7=#Cnc^jX);5P>sR?b!]~,Pd_>pQQ<' );
define( 'SECURE_AUTH_SALT', '9F7j^,md!j^Wb`#[CyvnP!{Ae+iCSrxUra=7kh>-{/puzu$Fj;F%ocS!Sp}W[~=P' );
define( 'LOGGED_IN_SALT',   '55LsSngz3];8:#7Qf?pc6>6Dzx@k8oqO-c}o}Cvk;HaUjMM2xS4)O(I-AlhWn@7#' );
define( 'NONCE_SALT',       '?%.x](%~mLk[2)c*Y&ZTFfm^7_c#$o1bztG~Xhg1kEmSI_3}2b&.,rDGi}~?E#u_' );

/**#@-*/

/**
 * WordPress database table prefix.
 *
 * You can have multiple installations in one database if you give each
 * a unique prefix. Only numbers, letters, and underscores please!
 */
$table_prefix = 'mh24_';

/**
 * For developers: WordPress debugging mode.
 *
 * Change this to true to enable the display of notices during development.
 * It is strongly recommended that plugin and theme developers use WP_DEBUG
 * in their development environments.
 *
 * For information on other constants that can be used for debugging,
 * visit the documentation.
 *
 * @link https://wordpress.org/documentation/article/debugging-in-wordpress/
 */
define( 'WP_DEBUG', true );
define( 'WP_DEBUG_LOG', true );
define( 'WP_DEBUG_DISPLAY', false );

/* Add any custom values between this line and the "stop editing" line. */



/* That's all, stop editing! Happy publishing. */

/** Absolute path to the WordPress directory. */
if ( ! defined( 'ABSPATH' ) ) {
	define( 'ABSPATH', __DIR__ . '/' );
}

/** Sets up WordPress vars and included files. */
require_once ABSPATH . 'wp-settings.php';

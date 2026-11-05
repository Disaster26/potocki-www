<?php
/**
 * Plugin Name:       Potocki static
 * Description:       Publikuje statyczna strone Potocki Dwor (katalog site/) w katalogu glownym WordPressa, dodaje przekierowania 301 ze starych adresow i strone 404. Dezaktywacja przywraca stara strone.
 * Version:           1.0.0
 * Requires at least: 5.6
 * Requires PHP:      7.2
 * Author:            Wylinka (wylinka.pl) dla Potocki Dwor
 * License:           GPL-2.0-or-later
 * Text Domain:       potocki-static
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'PDS_VERSION', '1.0.0' );
define( 'PDS_FILE', __FILE__ );
define( 'PDS_DIR', __DIR__ );
define( 'PDS_OPTION', 'potocki_static_state' );
define( 'PDS_MARK_BEGIN', '# BEGIN POTOCKI-STATIC' );
define( 'PDS_MARK_END', '# END POTOCKI-STATIC' );
define( 'PDS_BACKUP', '.htaccess.bak-potocki' );

/* ------------------------------------------------------------------ formularze strony (05.11.2026)
 * /wyslij.php nie istnieje jako plik (wtyczka nie kopiuje PHP), wiec zapytanie trafia do WordPressa. Tu, zanim WordPress
 * zacznie budowac strone, przechwytujemy te sciezke i obslugujemy formularz (wyslij.php z wtyczki: przyjecia, catering, hotel, biznes, kontakt). Bez FTP.
 */
add_action(
	'plugins_loaded',
	function () {
		$path = isset( $_SERVER['REQUEST_URI'] ) ? (string) wp_parse_url( (string) $_SERVER['REQUEST_URI'], PHP_URL_PATH ) : ''; // phpcs:ignore
		if ( '/wyslij.php' === $path && is_readable( PDS_DIR . '/wyslij.php' ) ) {
			if ( function_exists( 'do_action' ) ) {
				do_action( 'litespeed_control_set_nocache', 'formularz Potocki Dwor' ); // LiteSpeed Cache: nie zapamietywac odpowiedzi
			}
			require PDS_DIR . '/wyslij.php';
			exit;
		}
	},
	0
);

/* ------------------------------------------------------------------ sciezki */

/** Katalog glowny WordPressa (realpath, ze slashem na koncu). */
function pds_root() {
	$r = realpath( ABSPATH );
	return $r ? trailingslashit( wp_normalize_path( $r ) ) : false;
}

/** Katalog site/ wewnatrz wtyczki. */
function pds_src() {
	$r = realpath( PDS_DIR . '/site' );
	return $r ? trailingslashit( wp_normalize_path( $r ) ) : false;
}

/** Czy $path (znormalizowana) lezy wewnatrz $base. */
function pds_inside( $path, $base ) {
	$path = wp_normalize_path( $path );
	return '' !== $base && 0 === strpos( $path, $base );
}

/** Dozwolona sciezka wzgledna pliku strony (bez .., bez plikow ukrytych, bez PHP). */
function pds_rel_ok( $rel ) {
	if ( '' === $rel || false !== strpos( $rel, '..' ) || false !== strpos( $rel, "\0" ) ) {
		return false;
	}
	foreach ( explode( '/', $rel ) as $seg ) {
		if ( '' === $seg || '.' === $seg[0] ) {
			return false;
		}
	}
	return ! preg_match( '/\.(php\d?|phtml|phar|htaccess|htpasswd|ini|sh|cgi|pl|py)$/i', $rel );
}

/** Lista plikow w site/ (sciezki wzgledne, separator /). */
function pds_list_source() {
	$src = pds_src();
	if ( ! $src || ! is_dir( $src ) ) {
		return new WP_Error( 'pds_nosrc', 'Brak katalogu site/ we wtyczce.' );
	}
	$out = array();
	$it  = new RecursiveIteratorIterator(
		new RecursiveDirectoryIterator( $src, FilesystemIterator::SKIP_DOTS ),
		RecursiveIteratorIterator::LEAVES_ONLY
	);
	foreach ( $it as $f ) {
		if ( $f->isLink() || ! $f->isFile() ) {
			continue;
		}
		$real = realpath( $f->getPathname() );
		if ( ! $real || ! pds_inside( $real, $src ) ) {
			continue;
		}
		$rel = substr( wp_normalize_path( $real ), strlen( $src ) );
		if ( pds_rel_ok( $rel ) ) {
			$out[] = $rel;
		}
	}
	sort( $out );
	return $out;
}

function pds_state() {
	$s = get_option( PDS_OPTION );
	if ( ! is_array( $s ) ) {
		$s = array();
	}
	return wp_parse_args(
		$s,
		array(
			'files'   => array(),
			'dirs'    => array(),
			'version' => '',
			'time'    => 0,
		)
	);
}

/* ------------------------------------------------------------------ kopiowanie */

/**
 * Kopiuje site/ do ABSPATH. Nie nadpisuje zadnego pliku, ktorego nie skopiowala wczesniej ta wtyczka.
 * Przy bledzie cofa to, co zdazyla skopiowac w tym przebiegu.
 *
 * @return true|WP_Error
 */
function pds_copy_site() {
	$root = pds_root();
	$src  = pds_src();
	if ( ! $root || ! $src ) {
		return new WP_Error( 'pds_paths', 'Nie mozna ustalic katalogu WordPressa albo katalogu site/.' );
	}
	$files = pds_list_source();
	if ( is_wp_error( $files ) ) {
		return $files;
	}
	if ( ! in_array( 'index.html', $files, true ) ) {
		return new WP_Error( 'pds_noindex', 'W site/ brakuje index.html.' );
	}
	$state = pds_state();
	$ours  = array_flip( $state['files'] );

	// 1) kontrola konfliktow, zanim cokolwiek zostanie zapisane
	$conflicts = array();
	foreach ( $files as $rel ) {
		$dst = $root . $rel;
		if ( file_exists( $dst ) || is_link( $dst ) ) {
			if ( ! isset( $ours[ $rel ] ) || is_link( $dst ) || is_dir( $dst ) ) {
				$conflicts[] = $rel;
			}
		}
		// katalog posredni nie moze byc plikiem ani dowiazaniem
		$parts = explode( '/', $rel );
		array_pop( $parts );
		$acc = '';
		foreach ( $parts as $p ) {
			$acc .= $p;
			if ( is_link( $root . $acc ) || ( file_exists( $root . $acc ) && ! is_dir( $root . $acc ) ) ) {
				$conflicts[] = $acc;
			}
			$acc .= '/';
		}
	}
	if ( $conflicts ) {
		$conflicts = array_unique( $conflicts );
		return new WP_Error(
			'pds_conflict',
			'Te pliki juz istnieja w katalogu WordPressa i nie naleza do wtyczki (nic nie zostalo nadpisane): ' . implode( ', ', array_slice( $conflicts, 0, 20 ) ) . ( count( $conflicts ) > 20 ? ' ...' : '' )
		);
	}
	if ( ! wp_is_writable( $root ) ) {
		return new WP_Error( 'pds_rw', 'Katalog WordPressa nie jest zapisywalny dla PHP.' );
	}

	// 2) kopiowanie
	$copied   = array();
	$new_dirs = $state['dirs'];
	foreach ( $files as $rel ) {
		$dst = $root . $rel;
		$dir = dirname( $dst );
		if ( ! is_dir( $dir ) ) {
			// zapamietaj kazdy tworzony poziom
			$todo = array();
			$d    = $dir;
			while ( ! is_dir( $d ) && pds_inside( $d . '/', $root ) && wp_normalize_path( $d ) . '/' !== $root ) {
				$todo[] = $d;
				$d      = wp_normalize_path( dirname( $d ) );
			}
			if ( ! wp_mkdir_p( $dir ) ) {
				pds_rollback( $copied, array_diff( $new_dirs, $state['dirs'] ) );
				return new WP_Error( 'pds_mkdir', 'Nie mozna utworzyc katalogu: ' . esc_html( $dir ) );
			}
			foreach ( $todo as $t ) {
				$new_dirs[] = substr( wp_normalize_path( $t ), strlen( $root ) );
			}
		}
		$real_dir = realpath( $dir );
		if ( ! $real_dir || ! pds_inside( trailingslashit( wp_normalize_path( $real_dir ) ), $root ) ) {
			pds_rollback( $copied, array_diff( $new_dirs, $state['dirs'] ) );
			return new WP_Error( 'pds_path', 'Niedozwolona sciezka: ' . esc_html( $rel ) );
		}
		$existed = file_exists( $dst );
		if ( ! @copy( $src . $rel, $dst ) ) { // phpcs:ignore WordPress.PHP.NoSilencedErrors
			pds_rollback( $copied, array_diff( $new_dirs, $state['dirs'] ) );
			return new WP_Error( 'pds_copy', 'Nie udalo sie skopiowac: ' . esc_html( $rel ) );
		}
		if ( ! $existed ) {
			$copied[] = $rel;
		}
	}

	// 3) pliki z poprzedniej wersji, ktorych nie ma w nowej
	$keep = array_flip( $files );
	foreach ( $state['files'] as $rel ) {
		if ( ! isset( $keep[ $rel ] ) ) {
			pds_delete_file( $rel );
		}
	}

	$new_dirs = array_values( array_unique( $new_dirs ) );
	update_option(
		PDS_OPTION,
		array(
			'files'   => $files,
			'dirs'    => $new_dirs,
			'version' => PDS_VERSION,
			'time'    => time(),
		),
		false
	);
	return true;
}

/** Usuwa jeden plik z listy wtyczki (tylko wewnatrz ABSPATH, nigdy pliki WordPressa). */
function pds_delete_file( $rel ) {
	$root = pds_root();
	if ( ! $root || ! pds_rel_ok( $rel ) ) {
		return false;
	}
	$dst = $root . $rel;
	if ( is_link( $dst ) || ! is_file( $dst ) ) {
		return false;
	}
	$real = realpath( $dst );
	if ( ! $real || ! pds_inside( $real, $root ) ) {
		return false;
	}
	return @unlink( $real ); // phpcs:ignore WordPress.PHP.NoSilencedErrors
}

/** Cofa nowe pliki i katalogi utworzone w nieudanym przebiegu. */
function pds_rollback( $copied, $dirs ) {
	foreach ( $copied as $rel ) {
		pds_delete_file( $rel );
	}
	pds_remove_dirs( array_values( $dirs ) );
}

/** Usuwa puste katalogi utworzone przez wtyczke (najglebsze najpierw). */
function pds_remove_dirs( $dirs ) {
	$root = pds_root();
	if ( ! $root ) {
		return;
	}
	usort(
		$dirs,
		function ( $a, $b ) {
			return substr_count( $b, '/' ) - substr_count( $a, '/' );
		}
	);
	foreach ( $dirs as $rel ) {
		if ( ! pds_rel_ok( $rel . '/x' ) ) {
			continue;
		}
		$d = $root . $rel;
		if ( is_dir( $d ) && ! is_link( $d ) ) {
			$real = realpath( $d );
			if ( $real && pds_inside( trailingslashit( wp_normalize_path( $real ) ), $root ) && trailingslashit( wp_normalize_path( $real ) ) !== $root ) {
				$items = scandir( $real );
				if ( is_array( $items ) && count( $items ) <= 2 ) {
					@rmdir( $real ); // phpcs:ignore WordPress.PHP.NoSilencedErrors
				}
			}
		}
	}
}

/** Usuwa wszystkie pliki z listy. */
function pds_remove_site() {
	$state = pds_state();
	foreach ( $state['files'] as $rel ) {
		pds_delete_file( $rel );
	}
	pds_remove_dirs( $state['dirs'] );
	delete_option( PDS_OPTION );
}

/* ------------------------------------------------------------------ .htaccess */

function pds_htaccess_path() {
	$root = pds_root();
	return $root ? $root . '.htaccess' : false;
}

/** Tresc bez bloku POTOCKI-STATIC. */
function pds_strip_block( $txt ) {
	$re = '/^[ \t]*' . preg_quote( PDS_MARK_BEGIN, '/' ) . '[ \t]*\r?\n.*?^[ \t]*' . preg_quote( PDS_MARK_END, '/' ) . '[ \t]*(?:\r?\n)*/ms';
	return preg_replace( $re, '', $txt );
}

function pds_block() {
	$f = PDS_DIR . '/htaccess-blok.txt';
	if ( ! is_readable( $f ) ) {
		return new WP_Error( 'pds_noblock', 'Brak pliku htaccess-blok.txt we wtyczce.' );
	}
	$b = (string) file_get_contents( $f ); // phpcs:ignore WordPress.WP.AlternativeFunctions
	$b = str_replace( array( PDS_MARK_BEGIN, PDS_MARK_END ), '', $b );
	return PDS_MARK_BEGIN . "\n" . rtrim( $b ) . "\n" . PDS_MARK_END . "\n\n";
}

/**
 * Wstawia blok na poczatek .htaccess (po zrobieniu kopii) albo go usuwa.
 *
 * @param bool $add true = dodaj/odswiez, false = usun.
 * @return true|WP_Error
 */
function pds_write_htaccess( $add ) {
	$path = pds_htaccess_path();
	if ( ! $path ) {
		return new WP_Error( 'pds_ht', 'Brak sciezki .htaccess.' );
	}
	$exists = file_exists( $path );
	if ( $exists && ( is_link( $path ) || ! is_file( $path ) ) ) {
		return new WP_Error( 'pds_ht', '.htaccess nie jest zwyklym plikiem.' );
	}
	$old = $exists ? (string) file_get_contents( $path ) : ''; // phpcs:ignore WordPress.WP.AlternativeFunctions
	if ( $exists && ! is_writable( $path ) ) {
		return new WP_Error( 'pds_ht', '.htaccess nie jest zapisywalny.' );
	}
	if ( ! $exists && ! wp_is_writable( dirname( $path ) ) ) {
		return new WP_Error( 'pds_ht', 'Nie mozna utworzyc .htaccess.' );
	}
	$rest = pds_strip_block( $old );
	if ( $add ) {
		$block = pds_block();
		if ( is_wp_error( $block ) ) {
			return $block;
		}
		$new = $block . ltrim( $rest, "\r\n" );
	} else {
		$new = $rest;
	}
	if ( $new === $old ) {
		return true;
	}
	// kopia przed zapisem; pierwsza, nietknieta wersja zostaje osobno
	if ( $exists ) {
		$dir = dirname( $path );
		if ( ! file_exists( $dir . '/' . PDS_BACKUP . '-oryginal' ) ) {
			@copy( $path, $dir . '/' . PDS_BACKUP . '-oryginal' ); // phpcs:ignore WordPress.PHP.NoSilencedErrors
		}
		if ( ! @copy( $path, $dir . '/' . PDS_BACKUP ) ) { // phpcs:ignore WordPress.PHP.NoSilencedErrors
			return new WP_Error( 'pds_bak', 'Nie udalo sie zrobic kopii .htaccess - nic nie zmieniono.' );
		}
	}
	$ok = file_put_contents( $path, $new, LOCK_EX ); // phpcs:ignore WordPress.WP.AlternativeFunctions
	if ( false === $ok ) {
		return new WP_Error( 'pds_ht', 'Zapis .htaccess nie powiodl sie.' );
	}
	clearstatcache( true, $path );
	return true;
}

function pds_block_present() {
	$path = pds_htaccess_path();
	if ( ! $path || ! is_readable( $path ) ) {
		return false;
	}
	return false !== strpos( (string) file_get_contents( $path ), PDS_MARK_BEGIN ); // phpcs:ignore WordPress.WP.AlternativeFunctions
}

/* ------------------------------------------------------------------ cache */

function pds_purge_cache() {
	do_action( 'litespeed_purge_all' ); // LiteSpeed Cache (lokalnie, bez zapytan zewnetrznych)
	if ( function_exists( 'wp_cache_flush' ) ) {
		wp_cache_flush();
	}
}

/* ------------------------------------------------------------------ warunki */

/** WordPress musi obslugiwac katalog glowny domeny (nie podkatalog). */
function pds_preflight() {
	if ( is_multisite() ) {
		return new WP_Error( 'pds_ms', 'Wtyczka nie obsluguje sieci WordPress (multisite).' );
	}
	$path = wp_parse_url( home_url( '/' ), PHP_URL_PATH );
	if ( '/' !== $path && '' !== (string) $path ) {
		return new WP_Error( 'pds_sub', 'Adres witryny wskazuje na podkatalog (' . esc_html( $path ) . '). Wtyczka zaklada WordPress w katalogu glownym domeny.' );
	}
	if ( ! function_exists( 'get_home_path' ) ) {
		require_once ABSPATH . 'wp-admin/includes/file.php';
	}
	$home = realpath( get_home_path() );
	$root = pds_root();
	if ( ! $home || trailingslashit( wp_normalize_path( $home ) ) !== $root ) {
		return new WP_Error( 'pds_home', 'Katalog witryny rozni sie od katalogu WordPressa - wtyczka nie zapisze plikow w ciemno.' );
	}
	return true;
}

/* ------------------------------------------------------------------ aktywacja / dezaktywacja */

function pds_fail( WP_Error $e ) {
	deactivate_plugins( plugin_basename( PDS_FILE ), true );
	wp_die(
		'<p><strong>Potocki static nie zostal wlaczony.</strong></p><p>' . esc_html( $e->get_error_message() ) . '</p>',
		'Potocki static',
		array( 'back_link' => true )
	);
}

function pds_activate() {
	if ( ! current_user_can( 'activate_plugins' ) ) {
		return;
	}
	$p = pds_preflight();
	if ( is_wp_error( $p ) ) {
		pds_fail( $p );
	}
	$r = pds_copy_site();
	if ( is_wp_error( $r ) ) {
		pds_fail( $r );
	}
	$h = pds_write_htaccess( true );
	if ( is_wp_error( $h ) ) {
		pds_remove_site();
		pds_fail( $h );
	}
	pds_purge_cache();
}
register_activation_hook( __FILE__, 'pds_activate' );

function pds_deactivate() {
	if ( ! current_user_can( 'activate_plugins' ) ) {
		return;
	}
	pds_write_htaccess( false );
	pds_remove_site();
	pds_purge_cache();
}
register_deactivation_hook( __FILE__, 'pds_deactivate' );

/* ------------------------------------------------------------------ 404 ze strony statycznej */

/* Nieistniejace adresy obsluguje WordPress (regula index.php), wiec tu podajemy 404.html z kodem 404. */
add_action(
	'template_redirect',
	function () {
		if ( ! is_404() || is_admin() ) {
			return;
		}
		$root = pds_root();
		$f    = $root ? $root . '404.html' : '';
		if ( $f && is_file( $f ) && ! is_link( $f ) ) {
			status_header( 404 );
			nocache_headers();
			header( 'Content-Type: text/html; charset=utf-8' );
			readfile( $f ); // phpcs:ignore WordPress.WP.AlternativeFunctions
			exit;
		}
	},
	0
);

/* ------------------------------------------------------------------ panel: Narzedzia -> Potocki static */

add_action(
	'admin_menu',
	function () {
		add_management_page( 'Potocki static', 'Potocki static', 'manage_options', 'potocki-static', 'pds_admin_page' );
	}
);

/** Sprawdza strone glowna i jeden stary adres (zapytanie tylko do wlasnej domeny). */
function pds_live_test() {
	$out  = array();
	$home = home_url( '/' );
	$r    = wp_remote_get(
		add_query_arg( 'sps', time(), $home ),
		array(
			'timeout'     => 15,
			'redirection' => 2,
			'headers'     => array( 'Cache-Control' => 'no-cache' ),
		)
	);
	if ( is_wp_error( $r ) ) {
		$out[] = array( false, 'Strona glowna: blad polaczenia - ' . $r->get_error_message() );
	} else {
		$code = wp_remote_retrieve_response_code( $r );
		$body = wp_remote_retrieve_body( $r );
		$new  = false !== strpos( $body, 'potocki-static' );
		$out[] = array( 200 === $code && $new, 'Strona glowna ' . $home . ': HTTP ' . $code . ( $new ? ' - NOWA strona statyczna' : ' - to NIE jest nowa strona (stara strona albo cache)' ) );
	}
	$old = home_url( '/index.html' );
	$r   = wp_remote_head( $old, array( 'timeout' => 15, 'redirection' => 0 ) );
	if ( is_wp_error( $r ) ) {
		$out[] = array( false, 'Przekierowanie /index.html: blad - ' . $r->get_error_message() );
	} else {
		$code = wp_remote_retrieve_response_code( $r );
		$loc  = (string) wp_remote_retrieve_header( $r, 'location' );
		$ok   = 301 === $code && '/' === (string) wp_parse_url( $loc, PHP_URL_PATH );
		$out[] = array( $ok, 'Adres /index.html: HTTP ' . $code . ( $loc ? ' -> ' . $loc : '' ) );
	}
	$r = wp_remote_head( home_url( '/sitemap.xml' ), array( 'timeout' => 15, 'redirection' => 0 ) );
	if ( ! is_wp_error( $r ) ) {
		$code  = wp_remote_retrieve_response_code( $r );
		$out[] = array( 200 === $code, 'Mapa strony /sitemap.xml: HTTP ' . $code );
	}
	return $out;
}

function pds_admin_page() {
	if ( ! current_user_can( 'manage_options' ) ) {
		wp_die( esc_html__( 'Brak uprawnien.' ) );
	}
	$msgs  = array();
	$tests = null;
	if ( 'POST' === ( isset( $_SERVER['REQUEST_METHOD'] ) ? $_SERVER['REQUEST_METHOD'] : '' ) && isset( $_POST['pds_action'] ) ) { // phpcs:ignore
		check_admin_referer( 'pds_admin', 'pds_nonce' );
		$action = sanitize_key( wp_unslash( $_POST['pds_action'] ) );
		if ( 'refresh' === $action ) {
			$p = pds_preflight();
			$r = is_wp_error( $p ) ? $p : pds_copy_site();
			if ( ! is_wp_error( $r ) ) {
				$r = pds_write_htaccess( true );
			}
			if ( is_wp_error( $r ) ) {
				$msgs[] = array( 'error', $r->get_error_message() );
			} else {
				pds_purge_cache();
				$msgs[] = array( 'success', 'Pliki strony i reguly .htaccess zostaly odswiezone.' );
			}
		} elseif ( 'test' === $action ) {
			$tests = pds_live_test();
		}
	}

	$state   = pds_state();
	$root    = pds_root();
	$missing = array();
	foreach ( $state['files'] as $rel ) {
		if ( ! is_file( $root . $rel ) ) {
			$missing[] = $rel;
		}
	}
	$src = pds_list_source();
	$src_n = is_wp_error( $src ) ? 0 : count( $src );
	?>
	<div class="wrap">
		<h1>Potocki static</h1>
		<?php foreach ( $msgs as $m ) : ?>
			<div class="notice notice-<?php echo esc_attr( $m[0] ); ?>"><p><?php echo esc_html( $m[1] ); ?></p></div>
		<?php endforeach; ?>
		<table class="widefat striped" style="max-width:820px">
			<tbody>
				<tr><th>Wersja wtyczki</th><td><?php echo esc_html( PDS_VERSION ); ?> (pliki skopiowane z wersji: <?php echo esc_html( $state['version'] ? $state['version'] : '-' ); ?>)</td></tr>
				<tr><th>Ostatnie kopiowanie</th><td><?php echo $state['time'] ? esc_html( wp_date( 'Y-m-d H:i', $state['time'] ) ) : '-'; ?></td></tr>
				<tr><th>Pliki strony w katalogu WordPressa</th><td><?php echo esc_html( count( $state['files'] ) ); ?> (w paczce wtyczki: <?php echo esc_html( $src_n ); ?>)<?php echo $missing ? ' - <strong>brakuje ' . esc_html( count( $missing ) ) . '</strong>: ' . esc_html( implode( ', ', array_slice( $missing, 0, 10 ) ) ) : ''; ?></td></tr>
				<tr><th>Blok w .htaccess</th><td><?php echo pds_block_present() ? 'jest (na poczatku pliku)' : '<strong>brak</strong>'; ?></td></tr>
				<tr><th>Kopia .htaccess</th><td><?php echo file_exists( $root . PDS_BACKUP ) ? esc_html( PDS_BACKUP ) : '-'; ?><?php echo file_exists( $root . PDS_BACKUP . '-oryginal' ) ? ', ' . esc_html( PDS_BACKUP . '-oryginal' ) . ' (stan sprzed wtyczki)' : ''; ?></td></tr>
				<tr><th>Katalog WordPressa</th><td><code><?php echo esc_html( (string) $root ); ?></code></td></tr>
			</tbody>
		</table>
		<form method="post" style="margin-top:18px;display:inline-block">
			<?php wp_nonce_field( 'pds_admin', 'pds_nonce' ); ?>
			<input type="hidden" name="pds_action" value="refresh">
			<?php submit_button( 'Odśwież pliki', 'primary', 'submit', false ); ?>
		</form>
		<form method="post" style="margin:18px 0 0 8px;display:inline-block">
			<?php wp_nonce_field( 'pds_admin', 'pds_nonce' ); ?>
			<input type="hidden" name="pds_action" value="test">
			<?php submit_button( 'Sprawdź stronę na żywo', 'secondary', 'submit', false ); ?>
		</form>
		<?php if ( is_array( $tests ) ) : ?>
			<h2>Wynik testu</h2>
			<ul>
				<?php foreach ( $tests as $t ) : ?>
					<li><?php echo $t[0] ? '&#9989; ' : '&#10060; '; ?><?php echo esc_html( $t[1] ); ?></li>
				<?php endforeach; ?>
			</ul>
		<?php endif; ?>
		<p style="max-width:820px;margin-top:24px">„Odśwież pliki” kopiuje ponownie katalog <code>site/</code> po wgraniu nowszej wersji wtyczki i odświeża reguły w <code>.htaccess</code>. Dezaktywacja wtyczki usuwa skopiowane pliki i blok z <code>.htaccess</code> - wraca poprzednia strona WordPressa. Panel <code>/wp-admin/</code> działa przez cały czas.</p>
	</div>
	<?php
}

/* link "Ustawienia" na liscie wtyczek */
add_filter(
	'plugin_action_links_' . plugin_basename( __FILE__ ),
	function ( $links ) {
		array_unshift( $links, '<a href="' . esc_url( admin_url( 'tools.php?page=potocki-static' ) ) . '">Panel</a>' );
		return $links;
	}
);

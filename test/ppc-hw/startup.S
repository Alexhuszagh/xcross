/*
 * crt0.S -- startup file for PowerPC systems.
 *
 * Copyright (c) 1995 Cygnus Support
 *
 * The authors hereby grant permission to use, copy, modify, distribute,
 * and license this software and its documentation for any purpose, provided
 * that existing copyright notices are retained in all copies and that this
 * notice is included verbatim in any distributions. No written agreement,
 * license, or royalty fee is required for any of the authorized uses.
 * Modifications to this software may be copyrighted by their authors
 * and need not follow the licensing terms described here, provided that
 * the new terms are clearly indicated on the first page of each file where
 * they apply.
 */

/* provided by the gnu-toolchain */
#include "ppc-asm.h"

	.file	"startup.S"
	.text
.Lptr:
	.globl	_Reset
	.type	_Reset,@function
_Reset:
	bl	.Laddr			/* get current address */
.Laddr:
	mflr	r4			/* real address of .Laddr */
	lwz	r0,(.Lstk-.Laddr)(r4)	/* stack address location */
	mr	sp,r0			/* use user defined stack */

	addi	sp,sp,-4		/* make sure we don't overwrite debug mem */
	lis	r0,0
	stw	r0,0(sp)		/* clear back chain */
	stwu	sp,-64(sp)		/* push another stack frame */

	
	/* Let her rip */

	bl	FUNC_NAME(main)
	/* return value from main is argument to exit */
	bl	FUNC_NAME(exit) 
	bl	FUNC_NAME(_Reset)

	trap


	
	.Lstk:
/*	.long	__stack*/
	.long	stack_top

